class Component:

    min_bid = 1
    minted = {}
    timestamp = 0
    auction_window = 3600
    last_cycle = -1
    current_cycle = 0
    accounts = {}
    reserve = 0

    def __init__(self, token):
        self.token = token

    def __call__(self, timestamp: int):
        self.timestamp = timestamp
        return self

    @property
    def cycle(self) -> int:
        cycle = int(int(self.timestamp) / self.auction_window)
        if cycle > self.current_cycle:
            self.update_status(cycle)
        return cycle

    @property
    def last_minted(self):
        return self.minted.get(self.last_cycle)

    def get_cycle(self, winner: str) -> list:
        return [
            c
            for c, v
            in self.minted.items()
            if v['sender'] == winner
        ]

    def send_token(self, sender, amount):
        if sender not in self.accounts:
            self.accounts[sender] = amount
        else:
            self.accounts[sender] += amount
        return False

    def burn_token(self, sender, amount) -> bool:
        if sender not in self.accounts:
            return False
        if not self.accounts[sender] >= amount:
            return False
        else:
            self.accounts[sender] -= amount
            return True

    def update_status(self, cycle):
        self.update_cycle(cycle)
        if not self.last_cycle > 0:
            self.record_minted()

    def update_cycle(self, cycle):
        self.last_cycle = self.current_cycle
        self.current_cycle = cycle

    def record_minted(self):
        self.send_token(self.last_minted['sender'], 1000)
        self.reserve += self.last_minted['bid']
        self.min_bid = self.last_minted['bid']

    def balance(self, sender) -> int:
        return self.accounts.get(sender, 0)

    def verify_bid(self, bid) -> bool:
        return bid > self.min_bid

    def update_auction(self, bid: int, sender: str) -> True:
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

    def auction(self, sender: str, bid: int) -> bool:
        return self.verify_bid(bid) and self.update_auction(bid, sender)

    def redeem(self, sender: str, quantity: int) -> int:
        redeemed = (self.min_bid / 1000 - quantity) * quantity / 2
        if not redeemed <= self.reserve:
            return False

        burned = self.burn_token(sender, quantity)
        if not burned:
            return False
        if burned:
            self.min_bid = self.min_bid - quantity
            self.reserve -= redeemed
            return redeemed
