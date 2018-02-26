NLT_accounts = {}
NLT_reserve = {}
NLT_components = {}
NLT_AUCTION_WINDOW = 600
NLT_REWARD = 1000


class Component:
    min_bid = float(1)
    timestamp = 0
    auction_window = NLT_AUCTION_WINDOW
    last_cycle = -1
    start_timestamp = -1

    def __init__(self, token):
        self.minted = {}
        NLT_reserve[token] = float(0)
        self.token = token
        self.reserves = NLT_reserve
        self.components = NLT_components
        self.components[token] = self
        self.accounts = NLT_accounts
        self.current_cycle = 0

    def __call__(self, timestamp: float):
        self.timestamp = int(str(int(timestamp))[:10])
        if self.start_timestamp == -1:
            self.start_timestamp = timestamp
        if self.cycle > self.current_cycle:
            print('%s:: New cycle %s <- %s' % (self.token, self.cycle, self.current_cycle))
            self.update_status()
        return self

    def __repr__(self):
        return '%s %s => %s NTL' % (self.reserve, self.token, self.total_supply)

    @property
    def reserve(self):
        return self.reserves[self.token]

    @reserve.setter
    def reserve(self, v):
        self.reserves[self.token] = v

    @property
    def cycle(self) -> float:
        return int((self.timestamp - self.start_timestamp) / self.auction_window)

    @property
    def last_minted(self):
        return self.minted.get(self.last_cycle)

    def get_redeem_amount(self, quantity):
        assert quantity % NLT_REWARD == 0
        ret = sum([v['bid'] for v in self.minted.values()][-(int(quantity / NLT_REWARD) + 1):])
        if ret > self.reserve:
            return 0
        return ret

    def get_cycle(self, winner: str) -> list:
        return [
            c
            for c, v
            in self.minted.items()
            if v['sender'] == winner
        ]

    def send_token(self, sender, amount):
        print('sent %s NTL to %s' % (amount, sender))
        if sender not in self.accounts:
            self.accounts[sender] = amount
        else:
            self.accounts[sender] += amount
        print('Current balance %s' % self.accounts)

        return False

    def burn_token(self, sender, amount) -> bool:
        if sender not in self.accounts:
            return False
        if not self.accounts[sender] >= amount:
            return False
        else:
            self.accounts[sender] -= amount
            return True

    def update_status(self):
        self.update_cycle(self.cycle)
        if self.last_cycle >= 0:
            self.record_minted()

    def update_cycle(self, cycle):
        self.last_cycle = self.current_cycle
        self.current_cycle = cycle

    def record_minted(self):
        if self.last_minted:
            print('Found last Winner')
            self.send_token(self.last_minted['sender'], NLT_REWARD)
            self.reserve = self.reserve + self.last_minted['bid']
            self.min_bid = self.last_minted['bid']

    def balance(self, sender) -> float:
        return self.accounts.get(sender, 0)

    @property
    def total_supply(self) -> float:
        return sum(list(self.accounts.values()))

    def verify_bid(self, bid) -> bool:
        return bid >= self.min_bid

    def update_auction(self, bid: float, sender: str) -> True:
        params = dict(
            bid=bid,
            sender=sender
        )

        if self.cycle not in self.minted:
            self.minted[self.cycle] = params
            return True
        elif bid > self.minted[self.cycle]['bid']:
            self.minted[self.cycle].update(**params)
            return True
        return False

    def auction(self, sender: str, bid: float) -> bool:
        bid = float(bid)
        ret = self.verify_bid(bid) and self.update_auction(bid, sender)
        return ret

    def redeem_all(self, sender) -> float:
        return self.redeem(sender, self.balance(sender))

    def redeem_unit(self, sender):
        print('redeeming NLT_REWARD for %s, reserve is %s' % (self.token, self.reserve))
        redeemed = self.min_bid
        if redeemed > self.reserve:
            return 0

        self.reserve = self.reserve - redeemed
        if self.burn_token(sender, NLT_REWARD):
            if len(self.minted) > 1:
                self.min_bid = list(self.minted.values())[-2]['bid']
                del self.minted[list(self.minted.keys())[-1]]
            else:
                self.min_bid = 1  # set to the inital value
            return redeemed
        else:
            print('out of balance', self.balance(sender))
            return 0

    def redeem(self, sender: str, quantity: float) -> float:
        assert quantity % NLT_REWARD == 0
        for _ in range(0, int(quantity / NLT_REWARD)):
            yield self.redeem_unit(sender)
