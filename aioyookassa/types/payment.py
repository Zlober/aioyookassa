import datetime
from typing import List

from pydantic import BaseModel, Field

from .enum import PaymentStatus, ReceiptRegistration, CancellationParty, CancellationReason, ConfirmationType


class Confirmation(BaseModel):
    """
    Confirmation
    """
    type: ConfirmationType
    enforce: bool | None = None
    locale: str | None = None
    return_url: str | None = None
    url: str | None = Field(None, alias='confirmation_url')


class PaymentAmount(BaseModel):
    """
    Payment amount
    """
    value: int | float
    currency: str


class Recipient(BaseModel):
    """
    Payment receiver
    """
    account_id: str
    gateway_id: str


class PayerBankDetails(BaseModel):
    """
    Bank details of the payer
    """
    full_name: str
    short_name: str
    address: str
    inn: str
    bank_name: str
    bank_branch: str
    bank_bik: str
    bank_account: str
    kpp: str | None = None


class VatData(BaseModel):
    """
    VAT data
    """
    type: str
    amount: PaymentAmount | None = None
    rate: str | None = None


class CardInfo(BaseModel):
    """
    Card information
    """
    first_six: str | None = Field(None, alias='first6')
    last_four: str = Field(..., alias='last4')
    expiry_year: str
    expiry_month: str
    card_type: str
    card_country: str | None = Field(None, alias='issuer_country')
    bank_name: str | None = Field(None, alias='issuer_name')
    source: str | None = None


class PaymentMethod(BaseModel):
    """
    Payment method
    """
    type: str
    id: str
    saved: bool
    title: str | None = None
    login: str | None = None
    card: CardInfo | None = None
    phone: str | None = None
    payer_bank_details: PayerBankDetails | None = None
    payment_purpose: str | None = None
    vat_data: VatData | None = None
    account_number: str | None = None


class CancellationDetails(BaseModel):
    party: CancellationParty
    reason: CancellationReason


class ThreeDSInfo(BaseModel):
    """
    3DS information
    """
    applied: bool


class AuthorizationDetails(BaseModel):
    transaction_identifier: str | None = Field(None, alias='rrn')
    authorization_code: str | None = Field(None, alias='auth_code')
    three_d_secure: ThreeDSInfo


class Transfer(BaseModel):
    account_id: str
    amount: PaymentAmount
    status: PaymentStatus
    fee_amount: PaymentAmount = Field(None, alias='platform_fee_amount')
    description: str | None = None
    metadata: dict | None = None


class Settlement(BaseModel):
    type: str
    amount: PaymentAmount


class Deal(BaseModel):
    id: str
    settlements: List[PaymentAmount]


class Payment(BaseModel):
    """
    Payment
    """
    id: str
    status: PaymentStatus
    amount: PaymentAmount
    income_amount: PaymentAmount | None = None
    description: str | None = None
    recipient: Recipient
    payment_method: PaymentMethod | None = None
    captured_at: datetime.datetime | None = None
    created_at: datetime.datetime
    expires_at: datetime.datetime | None = None
    confirmation: Confirmation | None = None
    test: bool
    refunded_amount: PaymentAmount | None = None
    paid: bool
    refundable: bool
    receipt_registration: ReceiptRegistration | None = None
    metadata: dict | None = None
    cancellation_details: CancellationDetails | None = None
    authorization_details: AuthorizationDetails | None = None
    transfers: List[Transfer] | None = None
    deal: Deal | None = None
    merchant_customer_id: str | None = None


class PaymentsList(BaseModel):
    """
    Payments list
    """
    list: List[Payment] = Field([], alias='items')
    cursor: str | None = None


class Customer(BaseModel):
    """
    Customer
    """
    full_name: str | None = None
    inn: str | None = None
    email: str | None = None
    phone: str | None = None


class MarkQuantity(BaseModel):
    """
    Mark quantity
    """
    numerator: int
    denominator: int


class MarkCodeInfo(BaseModel):
    """
    Mark code information
    """
    code: str | None = Field(None, alias='mark_code_raw')
    unknown: str | None = None
    ean_8: str | None = None
    ean_13: str | None = None
    itf_14: str | None = None
    gs_10: str | None = None
    gs_1m: str | None = None
    short: str | None = None
    fur: str | None = None
    egais_20: str | None = None
    egais_30: str | None = None


class IndustryDetails(BaseModel):
    """
    Industry details
    """
    federal_id: str
    document_date: datetime.datetime
    document_number: str
    value: str


class PaymentItem(BaseModel):
    """
    Payment items
    """
    description: str
    amount: PaymentAmount
    vat_code: int
    quantity: str
    measure: str | None = None
    mark_quantity: MarkQuantity | None = None
    payment_subject: str | None = None
    payment_mode: str | None = None
    country_of_origin_code: str | None = None
    customs_declaration_number: str | None = None
    excise: str | None = None
    product_code: str | None = None
    mark_code_info: MarkCodeInfo | None = None
    mark_mode: str | None = None
    payment_subject_industry_details: IndustryDetails | None = None


class OperationDetails(BaseModel):
    """
    Operation details
    """
    id: int = Field(..., alias='operation_id')
    value: str
    created_at: datetime.datetime


class Receipt(BaseModel):
    """
    Receipt
    """
    customer: Customer | None = None
    items: List[PaymentItem]
    phone: str | None = None
    email: str | None = None
    tax_system_code: int | None = None
    receipt_industry_details: IndustryDetails | None = None
    receipt_operation_details: OperationDetails | None = None


class Passenger(BaseModel):
    first_name: str
    last_name: str


class Flight(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_date: datetime.datetime
    carrier_code: str | None = None


class Airline(BaseModel):
    """
    Airline
    """
    ticket_number: str | None = None
    booking_reference: str | None = None
    passengers: List[Passenger] | None = None
    flights: List[Flight] | None = Field(None, alias='legs')