from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Logo
from website.models import WebsiteURL
from .search_logo import find_logo_clearbit, find_logo_from_html
from .utils import download_image_from_url, resize_image, encode_image_to_base64


@shared_task
def search_logo_for_site(site_id):
  try:
    site = WebsiteURL.objects.get(id=site_id)
  except WebsiteURL.DoesNotExist:
    return f"Site {site_id} not found!"

  three_months_ago = timezone.now() - timedelta(days=90)
  last_logo = Logo.objects.filter(website=site).order_by('-created').first()

  if last_logo and last_logo.created >= three_months_ago:
    return f"Logo already exists for site {site.url}."


  clearbit_logo_url = find_logo_clearbit(site.url)
  html_logo_url = find_logo_from_html(site.url)

  logo_url = clearbit_logo_url or html_logo_url

  if logo_url:
    image_bytes = download_image_from_url(logo_url)
    if not image_bytes:
      return f"Failed to download logo from {logo_url}"

    resized_image_bytes = resize_image(image_bytes, size=(64, 64))
    if not resized_image_bytes:
      return f"Failed to resize logo from {logo_url}"

    image_base64 = encode_image_to_base64(resized_image_bytes)
    if not image_base64:
      return f"Failed to encode logo to Base64 from {logo_url}"

    if last_logo:
      last_logo.path = logo_url
      last_logo.original_url = logo_url
      last_logo.source = Logo.CLEARBIT if clearbit_logo_url else Logo.HTML_PARSER
      last_logo.image_base64 = image_base64
      last_logo.created = timezone.now()
      last_logo.version += 1
      last_logo.save()
      return f"Logo for {site.url} updated."
    else:
      Logo.objects.create(
        title=f"Logo for {site.url}",
        path=logo_url,
        original_url=logo_url,
        source=Logo.CLEARBIT if clearbit_logo_url else Logo.HTML_PARSER,
        website=site,
        version=1,
        image_base64=image_base64
      )
      return f"Logo saved with Base64 for site {site.url}"

  return f"No logo found for site {site.url}"


@shared_task
def update_old_logos():
  ninety_days_ago = timezone.now() - timedelta(days=90)

  outdated_sites = (
      WebsiteURL.objects
      .filter(logo__created__lt=ninety_days_ago)
      .distinct()
  )

  for site in outdated_sites:
      search_logo_for_site.delay(site.id)

  return f"Updated: {outdated_sites.count()} sites with outdated logos"


