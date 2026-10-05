import json
import boto3
import requests
from datetime import datetime
from lxml import html

s3 = boto3.client("s3")
BUCKET = "shiwani-flipkart-data-2026"

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.flipkart.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36',
}


def get_product_links(query, limit):
    products, seen = [], set()
    page = 1
    while len(products) < limit:
        params = {"q": query, "marketplace": "FLIPKART", "page": page}
        r = requests.get("https://www.flipkart.com/search",
                         params=params, headers=HEADERS, timeout=20)
        tree = html.fromstring(r.text)
        script = tree.xpath('//script[@id="jsonLD" and @type="application/ld+json"]/text()')
        if not script:
            break
        items = json.loads(script[0])[0].get("itemListElement", [])
        if not items:
            break
        for p in items:
            url = p.get("url")
            if url and url not in seen:
                seen.add(url)
                products.append({"name": p.get("name"), "url": url})
        page += 1
    return products[:limit]


def get_product_details(product):
    r = requests.get(product["url"], headers=HEADERS, timeout=20)
    tree = html.fromstring(r.text)
    price = rating = reviews = None

    for s in tree.xpath('//script[@type="application/ld+json"]/text()'):
        try:
            data = json.loads(s)
            if isinstance(data, list):
                data = next((d for d in data if isinstance(d, dict) and d.get("@type") == "Product"), None)
            if not data or data.get("@type") != "Product":
                continue
            offers = data.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            price = offers.get("price")
            agg = data.get("aggregateRating", {})
            rating = agg.get("ratingValue")
            reviews = agg.get("reviewCount")
            break
        except Exception:
            continue

    return {**product, "price": price, "rating": rating, "reviews": reviews}


def lambda_handler(event, context):
    query = event.get("query", "shoes")
    limit = int(event.get("limit", 10))

    results = []
    for p in get_product_links(query, limit):
        try:
            results.append(get_product_details(p))
        except Exception as e:
            print(f"Error: {p['url']} -> {e}")

    key = f"flipkart/{query}/{datetime.utcnow():%Y-%m-%d_%H-%M-%S}.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(results, ensure_ascii=False, indent=4).encode("utf-8"),
        ContentType="application/json",
    )
    return {"statusCode": 200, "saved_to": f"s3://{BUCKET}/{key}", "count": len(results)}