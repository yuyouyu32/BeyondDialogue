class Cost:
    def __init__(self, input_tokens_k: float = 0, output_tokens_k: float = 0 , money: float = 0, currency: str = 'RMB'):
        self.money = money
        self.input_tokens_k = input_tokens_k
        self.output_tokens_k = output_tokens_k
        self.currency = currency
    
    def _unit_currency(self, other: 'Cost'):
        if other.currency != self.currency:
            if other.currency == 'USD' and self.currency == 'RMB':
                money = other.money * 6.5
            elif other.currency == 'RMB' and self.currency == 'USD':
                money = other.money / 6.5
        else:
            money = other.money
        return money
        
    def __add__(self, other):
        if isinstance(other, Cost):
            money = self._unit_currency(other)
            return Cost(self.input_tokens_k + other.input_tokens_k, self.output_tokens_k + other.output_tokens_k, self.money + money)
        else:
            raise ValueError("Can only add Cost to another Cost")

    def __sub__(self, other):
        if isinstance(other, Cost):
            money = self._unit_currency(other)
            return Cost(self.input_tokens_k - other.input_tokens_k, self.output_tokens_k - other.output_tokens_k, self.money - money)
        else:
            raise ValueError("Can only subtract Cost from another Cost")

    def __str__(self):
        return f"Money: {self.money} {self.currency}, Input Tokens: {self.input_tokens_k}k, Output Tokens: {self.output_tokens_k}k"
    
    def __iter__(self):
        yield 'money', self.money
        yield 'input_tokens_k', self.input_tokens_k
        yield 'output_tokens_k', self.output_tokens_k
        yield 'currency', self.currency