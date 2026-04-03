"""
test_coin_collection.py
=======================
Regression tests for HorseGame coin collection.

Verifies two properties:

  1. COUNT  – For each NF level 0.1–1.0, exactly the right number of coins
              are collected (NF 0.3 → 3 coins, NF 0.9 → 9 coins, etc.).

  2. PHASE  – All eligible coins are collected in ONE batch during the jump
              arc, NOT split across a jump phase and a landing/cleanup phase.

The coin-collection functions in main.py are nested inside runMainGame() and
reference closure variables (gp, soundSystem), so they cannot be imported
directly without launching the full game.  The logic is therefore copied here
verbatim.  If you change checkForCoinCollision() or collectCoinsBasedOnNFPerformance()
in main.py, mirror the change here so the tests stay meaningful.

Run with:
    conda run -n fishgame3.7.5 python -m pytest HorseGame/test_coin_collection.py -v
"""

import pytest


# ─── Minimal fakes ────────────────────────────────────────────────────────────

class FakeRect:
    def __init__(self, left, top, width=40, height=40):
        self.left  = left
        self.top   = top
        self.width = width
        self.height = height

    @property
    def right(self):  return self.left + self.width
    @property
    def bottom(self): return self.top  + self.height
    @property
    def centery(self): return self.top + self.height // 2

    def colliderect(self, other):
        return (self.left < other.right and self.right > other.left and
                self.top  < other.bottom and self.bottom > other.top)


class FakeSpriteGroup:
    """Behaves like pygame.sprite.Group: kill() removes a sprite immediately."""
    def __init__(self, sprites=()):
        self._sprites = list(sprites)

    def __iter__(self):
        return iter(list(self._sprites))   # copy so mutations during iteration are safe

    def __len__(self):
        return len(self._sprites)

    def __bool__(self):
        return bool(self._sprites)

    def _remove(self, sprite):
        if sprite in self._sprites:
            self._sprites.remove(sprite)


class FakeCoin:
    COIN_WIDTH  = 40
    COIN_HEIGHT = 40
    COIN_LEFT   = 700          # x position where coins stop (roughly SCREEN_WIDTH / 1.6)

    def __init__(self, rank, centery, group):
        self.rank   = rank
        self._group = group
        self._killed = False
        top = centery - self.COIN_HEIGHT // 2
        self.rect = FakeRect(left=self.COIN_LEFT, top=top,
                             width=self.COIN_WIDTH, height=self.COIN_HEIGHT)

    def kill(self):
        self._killed = True
        self._group._remove(self)


class FakePlayer:
    HORSE_WIDTH  = 100
    HORSE_HEIGHT = 192

    def __init__(self, rect_right, rect_top, is_jumping=True):
        self.HorseIsJumping    = is_jumping
        self.HorseIsJumpingUp  = is_jumping
        self.HorseIsJumpingDown = False
        left = rect_right - self.HORSE_WIDTH
        self.rect = FakeRect(left=left, top=rect_top,
                             width=self.HORSE_WIDTH, height=self.HORSE_HEIGHT)


class FakeGP:
    """Minimal stand-in for GameParameters with only coin-related fields."""
    def __init__(self, coin_group, coins_to_collect, total=10):
        self.coin                    = coin_group
        self.coins_to_collect_this_jump   = coins_to_collect
        self.coins_that_should_be_collected = coins_to_collect
        self.totalNumCoins           = total
        self.coinsBeingCounted       = False
        self.boringMode              = True       # silences sound calls
        self.TASK_counter            = 1
        self.nrCoinsCollectedThroughoutRun = 0
        self.coinsCollectedInCurrentTrial  = 0
        self.nrCoinsPerTrial         = [0] * 10
        self.currentTime_s           = 0.0
        self.player                  = None       # set after construction


# ─── Logic copied from main.py ────────────────────────────────────────────────
# IMPORTANT: keep these in sync with checkForCoinCollision() and
# collectCoinsBasedOnNFPerformance() inside runMainGame() in main.py.

def _coin_collection_admin(gp):
    gp.nrCoinsCollectedThroughoutRun      += 1
    gp.coinsCollectedInCurrentTrial       += 1
    gp.nrCoinsPerTrial[gp.TASK_counter - 1] += 1


def _check_for_coin_collision(gp):
    """Coin collection dispatcher (from checkForCoinCollision)."""
    if gp.player.HorseIsJumping:
        eligible_coins = [c for c in gp.coin if c.rank <= gp.coins_to_collect_this_jump]
        if eligible_coins:
            top_coin = min(eligible_coins, key=lambda c: c.rect.centery)
            # x-only check: horse reaches the column on the descent, after the peak
            if gp.player.rect.right >= top_coin.rect.left:
                for coin in eligible_coins:
                    coin.kill()
                    _coin_collection_admin(gp)
        return

    if gp.coinsBeingCounted:
        gp.coinsBeingCounted = False
        return


# ─── Helpers FOR TESTING ──────────────────────────────────────────────────────────────────

COIN_BASE_Y  = 520   # centery of rank-1 coin (lowest on screen)
COIN_STEP_Y  = 50    # pixels between successive coins

def make_coins(n_total=10):
    """Return (FakeSpriteGroup, list[FakeCoin]).
    Rank 1 = lowest coin (highest centery), rank n_total = highest coin (lowest centery)."""
    group = FakeSpriteGroup()
    coins = []
    for rank in range(1, n_total + 1):
        centery = COIN_BASE_Y - (rank - 1) * COIN_STEP_Y
        coin = FakeCoin(rank=rank, centery=centery, group=group)
        coins.append(coin)
        group._sprites.append(coin)
    return group, coins


def make_player_at_peak(coins_to_collect, all_coins):
    """Horse at coin column x AND at the height of the highest eligible coin."""
    eligible = [c for c in all_coins if c.rank <= coins_to_collect]
    top_coin = min(eligible, key=lambda c: c.rect.centery)
    player_top   = top_coin.rect.centery - 5   # just above top coin
    player_right = FakeCoin.COIN_LEFT + 10     # past coin column left edge
    return FakePlayer(rect_right=player_right, rect_top=player_top, is_jumping=True)


def make_player_descending_at_coin_column(coins_to_collect, all_coins):
    """Horse at coin column x but BELOW the top eligible coin — simulates the real
    game where the horse reaches the column on the descent, after the peak."""
    eligible = [c for c in all_coins if c.rank <= coins_to_collect]
    top_coin = min(eligible, key=lambda c: c.rect.centery)
    # Horse top well below the top coin (has already descended past it)
    player_top   = top_coin.rect.centery + 150
    player_right = FakeCoin.COIN_LEFT + 10
    return FakePlayer(rect_right=player_right, rect_top=player_top, is_jumping=True)


# ─── Tests ────────────────────────────────────────────────────────────────────

NF_LEVELS = [(round(i * 0.1, 1), i) for i in range(1, 11)]
# [(0.1, 1), (0.2, 2), ..., (1.0, 10)]


@pytest.mark.parametrize("nf_level,expected_coins", NF_LEVELS)
def test_correct_coin_count(nf_level, expected_coins):
    """NF level X should result in exactly round(X*10) coins collected."""
    group, coins = make_coins()
    player = make_player_at_peak(expected_coins, coins)
    gp = FakeGP(group, coins_to_collect=expected_coins)
    gp.player = player

    _check_for_coin_collision(gp)

    assert gp.nrCoinsCollectedThroughoutRun == expected_coins, (
        f"NF={nf_level}: collected {gp.nrCoinsCollectedThroughoutRun}, expected {expected_coins}"
    )


@pytest.mark.parametrize("nf_level,expected_coins", NF_LEVELS)
def test_correct_coins_are_collected(nf_level, expected_coins):
    """The LOWEST-ranked coins (1..N) must be collected, not the top ones."""
    group, coins = make_coins()
    player = make_player_at_peak(expected_coins, coins)
    gp = FakeGP(group, coins_to_collect=expected_coins)
    gp.player = player

    _check_for_coin_collision(gp)

    killed_ranks    = {c.rank for c in coins if c._killed}
    surviving_ranks = {c.rank for c in coins if not c._killed}
    expected_killed = set(range(1, expected_coins + 1))

    assert killed_ranks == expected_killed, (
        f"NF={nf_level}: wrong coins collected. "
        f"Killed: {sorted(killed_ranks)}, expected: {sorted(expected_killed)}"
    )
    assert surviving_ranks == set(range(expected_coins + 1, 11)), (
        f"NF={nf_level}: wrong coins survived. Got: {sorted(surviving_ranks)}"
    )


@pytest.mark.parametrize("nf_level,expected_coins", NF_LEVELS)
def test_single_phase_collection(nf_level, expected_coins):
    """
    ALL eligible coins must be collected during the jump arc (phase 1).
    The landing cleanup (phase 2) must collect ZERO additional coins.

    This is the regression test for the two-phase bug where bottom coins
    disappeared during the jump and upper coins disappeared only after landing.
    """
    group, coins = make_coins()
    player = make_player_at_peak(expected_coins, coins)
    gp = FakeGP(group, coins_to_collect=expected_coins)
    gp.player = player

    # Phase 1 – horse is in the air, reaches coin column
    _check_for_coin_collision(gp)
    collected_during_jump = gp.nrCoinsCollectedThroughoutRun

    # Phase 2 – simulate horse landing
    player.HorseIsJumping     = False
    player.HorseIsJumpingUp   = False
    player.HorseIsJumpingDown = False
    gp.coinsBeingCounted      = True
    _check_for_coin_collision(gp)
    collected_after_landing = gp.nrCoinsCollectedThroughoutRun - collected_during_jump

    assert collected_during_jump == expected_coins, (
        f"NF={nf_level}: jump phase collected {collected_during_jump}, expected {expected_coins}"
    )
    assert collected_after_landing == 0, (
        f"NF={nf_level}: TWO-PHASE BUG — landing phase collected {collected_after_landing} "
        f"extra coin(s) that should have been collected during the jump"
    )


@pytest.mark.parametrize("nf_level,expected_coins", NF_LEVELS)
def test_arc_fires_when_horse_descending(nf_level, expected_coins):
    """
    Coins must be collected even when the horse reaches the coin column on the
    DESCENT (i.e. the horse top is already below the top eligible coin's centery).

    This is the regression test for the bug where the arc condition included a
    height check (rect.top <= top_coin.rect.centery) that was never True by the
    time the horse reached the coin column.
    """
    group, coins = make_coins()
    player = make_player_descending_at_coin_column(expected_coins, coins)
    gp = FakeGP(group, coins_to_collect=expected_coins)
    gp.player = player

    _check_for_coin_collision(gp)

    assert gp.nrCoinsCollectedThroughoutRun == expected_coins, (
        f"NF={nf_level}: arc did not fire on descent — "
        f"collected {gp.nrCoinsCollectedThroughoutRun}, expected {expected_coins}"
    )


@pytest.mark.parametrize("trial1_nf,trial2_nf", [
    (0.3, 0.5), (0.5, 0.3), (0.1, 1.0), (1.0, 0.1), (0.6, 0.6),
])
def test_multi_trial_correct_count(trial1_nf, trial2_nf):
    """
    After trial 1, coinsCollectedInCurrentTrial must be reset to 0 at the
    start of the next jump so the safety-net math stays correct in trial 2.

    Mirrors what main.py does: gp.coinsCollectedInCurrentTrial = 0 is set
    whenever a new jump event is triggered.
    """
    trial1_coins = round(trial1_nf * 10)
    trial2_coins = round(trial2_nf * 10)

    # ── Trial 1 ──────────────────────────────────────────────────────────────
    group1, coins1 = make_coins()
    player1 = make_player_at_peak(trial1_coins, coins1)
    gp = FakeGP(group1, coins_to_collect=trial1_coins)
    gp.player = player1
    _check_for_coin_collision(gp)
    assert gp.nrCoinsCollectedThroughoutRun == trial1_coins

    # ── Reset at jump start (mirrors main.py line added for this fix) ────────
    gp.coinsCollectedInCurrentTrial = 0

    # ── Trial 2 ──────────────────────────────────────────────────────────────
    group2, coins2 = make_coins()
    player2 = make_player_at_peak(trial2_coins, coins2)
    gp.coin = group2
    gp.coins_to_collect_this_jump = trial2_coins
    gp.player = player2
    _check_for_coin_collision(gp)

    assert gp.nrCoinsCollectedThroughoutRun == trial1_coins + trial2_coins, (
        f"Trial 1 (NF={trial1_nf}) + Trial 2 (NF={trial2_nf}): "
        f"expected {trial1_coins + trial2_coins} total, "
        f"got {gp.nrCoinsCollectedThroughoutRun}"
    )
    assert gp.coinsCollectedInCurrentTrial == trial2_coins, (
        f"coinsCollectedInCurrentTrial should be {trial2_coins} after trial 2, "
        f"got {gp.coinsCollectedInCurrentTrial} — stale value from trial 1?"
    )
