"""
eBay Trading API client — creates fixed-price BuyItNow listings via Auth'n'Auth token.
Uses the XML Trading API (site ID 3 = eBay UK) rather than the REST Inventory API,
which requires OAuth. Auth'n'Auth tokens (v^1.1 format) work here without extra setup.
"""
import logging
import re
import textwrap
from typing import Optional
from xml.sax.saxutils import escape as xml_escape

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

TRADING_API = "https://api.ebay.com/ws/api.dll"
SITE_ID     = "3"       # eBay UK
API_VERSION = "1155"
CATEGORY_ID = "15687"   # T-Shirts, eBay UK


class EbayClient:
    def __init__(self):
        self._token = settings.ebay_access_token

    def _headers(self, call: str) -> dict:
        return {
            "X-EBAY-API-COMPATIBILITY-LEVEL": API_VERSION,
            "X-EBAY-API-SITEID": SITE_ID,
            "X-EBAY-API-CALL-NAME": call,
            "X-EBAY-API-APP-NAME":  settings.ebay_app_id,
            "X-EBAY-API-DEV-NAME":  settings.ebay_dev_id,
            "X-EBAY-API-CERT-NAME": settings.ebay_cert_id,
            "X-EBAY-API-IAFTOKEN":  self._token,
            "Content-Type": "text/xml",
        }

    async def create_listing(
        self,
        title: str,
        description: str,
        price_gbp: float,
        image_url: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a fixed-price BuyItNow listing on eBay UK.
        Returns the ItemID string on success, None on failure.
        """
        if not self._token:
            logger.warning("eBay: no access token — skipping listing")
            return None

        title = xml_escape(title[:80])
        pic_xml = f"<PictureURL>{xml_escape(image_url)}</PictureURL>" if image_url else ""

        xml = textwrap.dedent(f"""
            <?xml version="1.0" encoding="utf-8"?>
            <AddFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>{self._token}</eBayAuthToken>
              </RequesterCredentials>
              <Item>
                <Title>{title}</Title>
                <Description><![CDATA[{description}]]></Description>
                <PrimaryCategory>
                  <CategoryID>{CATEGORY_ID}</CategoryID>
                </PrimaryCategory>
                <StartPrice currencyID="GBP">{price_gbp:.2f}</StartPrice>
                <ConditionID>1000</ConditionID>
                <Country>GB</Country>
                <Currency>GBP</Currency>
                <DispatchTimeMax>5</DispatchTimeMax>
                <ListingDuration>GTC</ListingDuration>
                <ListingType>FixedPriceItem</ListingType>
                <Quantity>999</Quantity>
                <PostalCode>{xml_escape(settings.ebay_postal_code)}</PostalCode>
                <ReturnPolicy>
                  <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
                  <ReturnsWithinOption>Days_30</ReturnsWithinOption>
                  <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
                </ReturnPolicy>
                <ShippingDetails>
                  <ShippingType>Flat</ShippingType>
                  <ShippingServiceOptions>
                    <ShippingServicePriority>1</ShippingServicePriority>
                    <ShippingService>UK_OtherCourier3Days</ShippingService>
                    <ShippingServiceCost currencyID="GBP">3.99</ShippingServiceCost>
                    <ShippingServiceAdditionalCost currencyID="GBP">1.00</ShippingServiceAdditionalCost>
                    <FreeShipping>false</FreeShipping>
                  </ShippingServiceOptions>
                </ShippingDetails>
                <PictureDetails>
                  {pic_xml}
                </PictureDetails>
                <ItemSpecifics>
                  <NameValueList>
                    <Name>Brand</Name>
                    <Value>NickPrintCo</Value>
                  </NameValueList>
                  <NameValueList>
                    <Name>Department</Name>
                    <Value>Unisex Adults</Value>
                  </NameValueList>
                  <NameValueList>
                    <Name>Type</Name>
                    <Value>T-Shirt</Value>
                  </NameValueList>
                  <NameValueList>
                    <Name>Size Type</Name>
                    <Value>Regular</Value>
                  </NameValueList>
                  <NameValueList>
                    <Name>Size</Name>
                    <Value>M</Value>
                  </NameValueList>
                  <NameValueList>
                    <Name>Colour</Name>
                    <Value>Multicolour</Value>
                  </NameValueList>
                </ItemSpecifics>
                <Site>UK</Site>
              </Item>
            </AddFixedPriceItemRequest>
        """).strip()

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    TRADING_API,
                    content=xml.encode("utf-8"),
                    headers=self._headers("AddFixedPriceItem"),
                )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("eBay HTTP error: %s", exc)
            return None

        body = resp.text

        if "<Ack>Failure</Ack>" in body or "<Ack>PartialFailure</Ack>" in body:
            short = re.findall(r"<ShortMessage>(.*?)</ShortMessage>", body)
            long_ = re.findall(r"<LongMessage>(.*?)</LongMessage>", body)
            msgs = long_ or short
            logger.error("eBay listing failed: %s", "; ".join(msgs) if msgs else body[:800])
            return None

        if "<Ack>Warning</Ack>" in body:
            warns = re.findall(r"<ShortMessage>(.*?)</ShortMessage>", body)
            logger.warning("eBay listing warnings: %s", "; ".join(warns))

        m = re.search(r"<ItemID>(\d+)</ItemID>", body)
        if not m:
            logger.error("eBay: no ItemID in response — %s", body[:500])
            return None

        item_id = m.group(1)
        logger.info("eBay listing created — ItemID %s", item_id)
        return item_id
