"""
eBay Trading API client — creates fixed-price BuyItNow listings via Auth'n'Auth token.
Uses the XML Trading API (site ID 3 = eBay UK) rather than the REST Inventory API,
which requires OAuth. Auth'n'Auth tokens (v^1.1 format) work here without extra setup.
"""
import logging
import re
import textwrap
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from xml.sax.saxutils import escape as xml_escape

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

TRADING_API = "https://api.ebay.com/ws/api.dll"
SITE_ID     = "3"       # eBay UK
API_VERSION = "1155"
CATEGORY_ID = "15687"   # T-Shirts, eBay UK

SIZES = ["S", "M", "L", "XL", "2XL"]

# Bella+Canvas 3001 white variant IDs: S=4012, M=4013, L=4014, XL=4015, 2XL=4016
SIZE_TO_VARIANT: Dict[str, int] = {
    "S": 4012, "M": 4013, "L": 4014, "XL": 4015, "2XL": 4016,
}


class EbayClient:
    def __init__(self):
        self._token = settings.ebay_access_token
        self._profiles: Dict[str, str] = {}  # payment_id, return_id, shipping_id

    async def _ensure_profiles(self) -> bool:
        """Fetch seller Business Policy IDs via GetUserPreferences. Cached after first call."""
        if self._profiles:
            return True

        xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<GetUserPreferencesRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            f"<RequesterCredentials><eBayAuthToken>{self._token}</eBayAuthToken></RequesterCredentials>"
            "<ShowSellerProfilePreferences>true</ShowSellerProfilePreferences>"
            "</GetUserPreferencesRequest>"
        )

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    TRADING_API,
                    content=xml.encode("utf-8"),
                    headers=self._headers("GetUserPreferences"),
                )
            body = resp.text
        except httpx.HTTPError as exc:
            logger.error("eBay GetUserPreferences HTTP error: %s", exc)
            return False

        if "<Ack>Failure</Ack>" in body:
            msgs = re.findall(r"<LongMessage>(.*?)</LongMessage>", body)
            logger.error("eBay GetUserPreferences failed: %s", "; ".join(msgs))
            return False

        # Parse SupportedSellerProfile blocks — each has ProfileType and ProfileID
        profiles: Dict[str, str] = {}
        for block in re.findall(r"<SupportedSellerProfile>(.*?)</SupportedSellerProfile>", body, re.DOTALL):
            pid_m = re.search(r"<ProfileID>(\d+)</ProfileID>", block)
            ptype_m = re.search(r"<ProfileType>(.*?)</ProfileType>", block)
            if pid_m and ptype_m:
                profiles[ptype_m.group(1)] = pid_m.group(1)

        if not all(k in profiles for k in ("PAYMENT", "RETURN_POLICY", "SHIPPING")):
            logger.error("eBay: missing policy types — found: %s", list(profiles.keys()))
            return False

        self._profiles = {
            "payment_id": profiles["PAYMENT"],
            "return_id":  profiles["RETURN_POLICY"],
            "shipping_id": profiles["SHIPPING"],
        }
        logger.info(
            "eBay seller profiles loaded — payment=%s return=%s shipping=%s",
            self._profiles["payment_id"],
            self._profiles["return_id"],
            self._profiles["shipping_id"],
        )
        return True

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

    def _variation_xml(self, price_gbp: float) -> str:
        size_values = "".join(f"<Value>{s}</Value>" for s in SIZES)
        variations = ""
        for size in SIZES:
            variations += textwrap.dedent(f"""
                <Variation>
                  <StartPrice currencyID="GBP">{price_gbp:.2f}</StartPrice>
                  <Quantity>999</Quantity>
                  <VariationSpecifics>
                    <NameValueList><Name>Size</Name><Value>{size}</Value></NameValueList>
                  </VariationSpecifics>
                </Variation>""")
        return f"""
        <Variations>
          <VariationSpecificsSet>
            <NameValueList><Name>Size</Name>{size_values}</NameValueList>
          </VariationSpecificsSet>
          {variations}
        </Variations>"""

    def _item_specifics_xml(self, specifics: list) -> str:
        return "".join(
            f"<NameValueList><Name>{xml_escape(n)}</Name><Value>{xml_escape(v)}</Value></NameValueList>"
            for n, v in specifics
        )

    async def create_listing(
        self,
        title: str,
        description: str,
        price_gbp: float,
        image_url: Optional[str] = None,
        category_id: str = CATEGORY_ID,
        has_sizes: bool = True,
        item_specifics: Optional[list] = None,
    ) -> Optional[str]:
        """
        Create a fixed-price BuyItNow listing on eBay UK.
        has_sizes=True adds S/M/L/XL/2XL variations (t-shirts, hoodies).
        has_sizes=False creates a single-quantity listing (mugs, totes).
        Returns the ItemID string on success, None on failure.
        """
        if not self._token:
            logger.warning("eBay: no access token — skipping listing")
            return None

        if not await self._ensure_profiles():
            logger.error("eBay: cannot create listing — seller profiles unavailable")
            return None

        title = xml_escape(title[:80])
        pic_xml = f"<PictureURL>{xml_escape(image_url)}</PictureURL>" if image_url else ""
        variation_xml = self._variation_xml(price_gbp) if has_sizes else ""
        quantity_xml = "" if has_sizes else "<Quantity>999</Quantity>"
        price_xml = "" if has_sizes else f'<StartPrice currencyID="GBP">{price_gbp:.2f}</StartPrice>'
        specifics_xml = self._item_specifics_xml(item_specifics) if item_specifics else self._item_specifics_xml([
            ("Brand", "NickPrintCo"), ("Department", "Unisex Adults"),
            ("Type", "T-Shirt"), ("Size Type", "Regular"), ("Colour", "White"),
        ])
        profiles = self._profiles

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
                  <CategoryID>{category_id}</CategoryID>
                </PrimaryCategory>
                {price_xml}
                <ConditionID>1000</ConditionID>
                <Country>GB</Country>
                <Currency>GBP</Currency>
                <DispatchTimeMax>5</DispatchTimeMax>
                <ListingDuration>GTC</ListingDuration>
                <ListingType>FixedPriceItem</ListingType>
                {quantity_xml}
                <PostalCode>{xml_escape(settings.ebay_postal_code)}</PostalCode>
                <SellerProfiles>
                  <SellerPaymentProfile>
                    <PaymentProfileID>{profiles['payment_id']}</PaymentProfileID>
                  </SellerPaymentProfile>
                  <SellerReturnProfile>
                    <ReturnProfileID>{profiles['return_id']}</ReturnProfileID>
                  </SellerReturnProfile>
                  <SellerShippingProfile>
                    <ShippingProfileID>{profiles['shipping_id']}</ShippingProfileID>
                  </SellerShippingProfile>
                </SellerProfiles>
                <PictureDetails>
                  {pic_xml}
                </PictureDetails>
                <ItemSpecifics>
                  {specifics_xml}
                </ItemSpecifics>
                {variation_xml}
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

    async def get_paid_orders(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch completed (paid) orders from the last `days_back` days.
        Returns a list of dicts with order details.
        """
        if not self._token:
            return []

        now = datetime.now(timezone.utc)
        from_dt = (now - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        to_dt = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        xml = textwrap.dedent(f"""
            <?xml version="1.0" encoding="utf-8"?>
            <GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>{self._token}</eBayAuthToken>
              </RequesterCredentials>
              <CreateTimeFrom>{from_dt}</CreateTimeFrom>
              <CreateTimeTo>{to_dt}</CreateTimeTo>
              <OrderStatus>Completed</OrderStatus>
              <Pagination>
                <EntriesPerPage>100</EntriesPerPage>
                <PageNumber>1</PageNumber>
              </Pagination>
            </GetOrdersRequest>
        """).strip()

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    TRADING_API,
                    content=xml.encode("utf-8"),
                    headers=self._headers("GetOrders"),
                )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("eBay GetOrders HTTP error: %s", exc)
            return []

        body = resp.text

        if "<Ack>Failure</Ack>" in body:
            msgs = re.findall(r"<LongMessage>(.*?)</LongMessage>", body)
            logger.error("eBay GetOrders failed: %s", "; ".join(msgs))
            return []

        orders = []
        for order_block in re.findall(r"<Order>(.*?)</Order>", body, re.DOTALL):
            order_id_m = re.search(r"<OrderID>(.*?)</OrderID>", order_block)
            if not order_id_m:
                continue

            addr = {}
            addr_block_m = re.search(r"<ShippingAddress>(.*?)</ShippingAddress>", order_block, re.DOTALL)
            if addr_block_m:
                ab = addr_block_m.group(1)
                addr = {
                    "name":    _extract(ab, "Name"),
                    "address1": _extract(ab, "Street1"),
                    "address2": _extract(ab, "Street2"),
                    "city":    _extract(ab, "CityName"),
                    "state":   _extract(ab, "StateOrProvince"),
                    "zip":     _extract(ab, "PostalCode"),
                    "country_code": _extract(ab, "Country") or "GB",
                }

            for tx_block in re.findall(r"<Transaction>(.*?)</Transaction>", order_block, re.DOTALL):
                item_id_m = re.search(r"<ItemID>(\d+)</ItemID>", tx_block)
                qty_m = re.search(r"<QuantityPurchased>(\d+)</QuantityPurchased>", tx_block)
                size_m = re.search(
                    r"<VariationSpecifics>.*?<Name>Size</Name>.*?<Value>(.*?)</Value>.*?</VariationSpecifics>",
                    tx_block, re.DOTALL,
                )
                tx_id_m = re.search(r"<TransactionID>(.*?)</TransactionID>", tx_block)
                orders.append({
                    "order_id": order_id_m.group(1),
                    "transaction_id": tx_id_m.group(1) if tx_id_m else "0",
                    "item_id": item_id_m.group(1) if item_id_m else "",
                    "quantity": int(qty_m.group(1)) if qty_m else 1,
                    "size": size_m.group(1) if size_m else "M",
                    **addr,
                })

        logger.info("eBay GetOrders: found %d transactions", len(orders))
        return orders


    async def mark_shipped(self, order_id: str, tracking_number: str, carrier: str) -> bool:
        """Post tracking to eBay via CompleteSale. Marks the order as dispatched."""
        carrier_codes = {
            "DPD": "UK_DPD", "Royal Mail": "UK_RoyalMail", "RoyalMail": "UK_RoyalMail",
            "DHL": "DHL_UK_DHL", "UPS": "UPS", "Evri": "UK_Hermes", "Hermes": "UK_Hermes",
            "FedEx": "FedEx", "Yodel": "UK_Yodel",
        }
        ebay_carrier = carrier_codes.get(carrier, "UK_OtherCourier")

        xml = textwrap.dedent(f"""
            <?xml version="1.0" encoding="utf-8"?>
            <CompleteSaleRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>{self._token}</eBayAuthToken>
              </RequesterCredentials>
              <OrderID>{xml_escape(order_id)}</OrderID>
              <Shipped>true</Shipped>
              <Shipment>
                <ShipmentTrackingDetails>
                  <ShipmentTrackingNumber>{xml_escape(tracking_number)}</ShipmentTrackingNumber>
                  <ShippingCarrierUsed>{ebay_carrier}</ShippingCarrierUsed>
                </ShipmentTrackingDetails>
              </Shipment>
            </CompleteSaleRequest>
        """).strip()

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    TRADING_API,
                    content=xml.encode("utf-8"),
                    headers=self._headers("CompleteSale"),
                )
            resp.raise_for_status()
            body = resp.text
            if "<Ack>Success</Ack>" in body or "<Ack>Warning</Ack>" in body:
                logger.info("eBay order %s marked as shipped (tracking: %s)", order_id, tracking_number)
                return True
            msgs = re.findall(r"<LongMessage>(.*?)</LongMessage>", body) or re.findall(r"<ShortMessage>(.*?)</ShortMessage>", body)
            logger.error("eBay CompleteSale failed: %s", "; ".join(msgs))
            return False
        except httpx.HTTPError as exc:
            logger.error("eBay CompleteSale HTTP error: %s", exc)
            return False


    async def end_listing(self, item_id: str, reason: str = "NotAvailable") -> bool:
        """End an active eBay listing immediately via EndFixedPriceItem."""
        xml = textwrap.dedent(f"""
            <?xml version="1.0" encoding="utf-8"?>
            <EndFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>{self._token}</eBayAuthToken>
              </RequesterCredentials>
              <ItemID>{xml_escape(item_id)}</ItemID>
              <EndingReason>{reason}</EndingReason>
            </EndFixedPriceItemRequest>
        """).strip()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    TRADING_API,
                    content=xml.encode("utf-8"),
                    headers=self._headers("EndFixedPriceItem"),
                )
            resp.raise_for_status()
            body = resp.text
            if "<Ack>Success</Ack>" in body or "<Ack>Warning</Ack>" in body:
                logger.info("eBay listing %s ended", item_id)
                return True
            msgs = re.findall(r"<LongMessage>(.*?)</LongMessage>", body)
            logger.error("eBay end_listing failed: %s", "; ".join(msgs))
            return False
        except httpx.HTTPError as exc:
            logger.error("eBay end_listing HTTP error: %s", exc)
            return False

    async def revise_quantity(self, item_id: str, quantity: int) -> bool:
        """Set listing quantity to pause/resume without ending it."""
        xml = textwrap.dedent(f"""
            <?xml version="1.0" encoding="utf-8"?>
            <ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>{self._token}</eBayAuthToken>
              </RequesterCredentials>
              <Item>
                <ItemID>{xml_escape(item_id)}</ItemID>
                <Quantity>{quantity}</Quantity>
              </Item>
            </ReviseFixedPriceItemRequest>
        """).strip()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    TRADING_API,
                    content=xml.encode("utf-8"),
                    headers=self._headers("ReviseFixedPriceItem"),
                )
            resp.raise_for_status()
            body = resp.text
            if "<Ack>Success</Ack>" in body or "<Ack>Warning</Ack>" in body:
                logger.info("eBay listing %s quantity set to %d", item_id, quantity)
                return True
            msgs = re.findall(r"<LongMessage>(.*?)</LongMessage>", body)
            logger.error("eBay revise_quantity failed: %s", "; ".join(msgs))
            return False
        except httpx.HTTPError as exc:
            logger.error("eBay revise_quantity HTTP error: %s", exc)
            return False


def _extract(xml_str: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", xml_str, re.DOTALL)
    return m.group(1).strip() if m else ""
