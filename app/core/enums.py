from enum import StrEnum


class KafkaTopicEnum(StrEnum):
    ANALYTICS = 'analytics-topic'
    AVRO = 'avro-example-topic'


class KafkaGroupEnum(StrEnum):
    ANALYTICS = 'analytics-group'
    AVRO = 'avro-example-group'


class CurrencyEnum(StrEnum):
    USD = 'USD'
    EUR = 'EUR'
    AUD = 'AUD'
    CAD = 'CAD'
    ARS = 'ARS'
    PLN = 'PLN'
    BTC = 'BTC'
    ETH = 'ETH'
    DOGE = 'DOGE'
    USDT = 'USDT'


class TransactionStatusEnum(StrEnum):
    PROCESSED = 'PROCESSED'
    ROLLBACKED = 'ROLLBACKED'


class UserStatusEnum(StrEnum):
    ACTIVE = 'ACTIVE'
    BLOCKED = 'BLOCKED'


EXCHANGE_RATES_TO_USD = {
    CurrencyEnum.USD: 1,
    CurrencyEnum.EUR: 0.9342,
    CurrencyEnum.AUD: 0.5447,
    CurrencyEnum.CAD: 0.6162,
    CurrencyEnum.ARS: 0.0009,
    CurrencyEnum.PLN: 0.2343,
    CurrencyEnum.BTC: 100000.0,
    CurrencyEnum.ETH: 3557.3476,
    CurrencyEnum.DOGE: 0.3627,
    CurrencyEnum.USDT: 0.9709,
}
