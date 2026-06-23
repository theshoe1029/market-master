#!/usr/bin/env python3
"""
Market Making Game — practice quoting bid/ask spreads on math estimation questions.

You are the market maker. The script acts as a counterparty that trades against
your quotes using a simple random-belief strategy (for now).
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Callable


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------

def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _count_primes(lo: int, hi: int) -> int:
    return sum(1 for n in range(lo, hi + 1) if _is_prime(n))


@dataclass(frozen=True)
class Question:
    prompt: str
    answer: float
    integer: bool = False

    @property
    def true_value(self) -> float:
        return float(self.answer)


QuestionFactory = Callable[[], Question]


def _random_non_square(lo: int = 2, hi: int = 250) -> int:
    while True:
        n = random.randint(lo, hi)
        if math.isqrt(n) ** 2 != n:
            return n


def _trig_prompt(fn: str, k: int, n: int) -> str:
    angle = f"π/{n}" if k == 1 else f"{k}π/{n}"
    return f"What is {fn}({angle})?"


def _gen_log10() -> Question:
    x = random.randint(2, 200)
    return Question(f"What is log₁₀({x})?", math.log10(x))


def _gen_ln() -> Question:
    x = random.randint(2, 80)
    return Question(f"What is ln({x})?", math.log(x))


def _gen_sqrt() -> Question:
    x = _random_non_square()
    return Question(f"What is √{x}?", math.sqrt(x))


def _gen_exp() -> Question:
    x = random.randint(1, 25) / 10  # 0.1 … 2.5
    return Question(f"What is e^{x:g}?", math.exp(x))


def _gen_sin() -> Question:
    n = random.randint(3, 17)
    k = random.randint(1, n - 1)
    return Question(_trig_prompt("sin", k, n), math.sin(k * math.pi / n))


def _gen_cos() -> Question:
    n = random.randint(4, 20)
    k = random.randint(1, n - 1)
    return Question(_trig_prompt("cos", k, n), math.cos(k * math.pi / n))


def _gen_tan() -> Question:
    while True:
        n = random.randint(5, 24)
        k = random.randint(1, n - 1)
        val = math.tan(k * math.pi / n)
        if math.isfinite(val) and abs(val) < 20:
            return Question(_trig_prompt("tan", k, n), val)


def _gen_power() -> Question:
    base = random.randint(2, 15)
    exp = random.randint(2, 9) / 10  # 0.2 … 0.9
    return Question(f"What is {base}^{exp:g}?", base ** exp)


def _gen_integer_power() -> Question:
    base = random.randint(2, 9)
    exp = random.randint(2, 5)
    return Question(f"What is {base}^{exp}?", float(base ** exp), integer=True)


MATH_GENERATORS: list[QuestionFactory] = [
    _gen_log10,
    _gen_ln,
    _gen_sqrt,
    _gen_exp,
    _gen_sin,
    _gen_cos,
    _gen_tan,
    _gen_power,
    _gen_integer_power,
]

STATIC_QUESTIONS: list[Question] = [
    Question(
        "How many prime numbers are there between 1 and 100?",
        float(_count_primes(1, 100)),
        integer=True,
    ),
    Question(
        "How many prime numbers are there between 50 and 200?",
        float(_count_primes(50, 200)),
        integer=True,
    ),
    Question(
        "How many perfect squares are there between 1 and 500?",
        float(int(math.isqrt(500))),
        integer=True,
    ),
    Question("What is ⌊1000 / 37⌋?", float(1000 // 37), integer=True),
    Question("What is the golden ratio φ = (1 + √5) / 2?", (1 + math.sqrt(5)) / 2),
]

# Canonical order-of-magnitude answers for Fermi-style estimation practice.
FERMI_QUESTIONS: list[Question] = [
    Question(
        "How many gas stations are there in the United States?",
        145_000,
        integer=True,
    ),
    Question(
        "How many piano tuners are there in New York City?",
        300,
        integer=True,
    ),
    Question(
        "How many golf balls fit in a standard school bus?",
        50_000,
        integer=True,
    ),
    Question(
        "How many hairs are on the average human head?",
        100_000,
        integer=True,
    ),
    Question(
        "How many miles of interstate highway are there in the United States?",
        47_000,
        integer=True,
    ),
    Question(
        "How many Starbucks locations are there worldwide?",
        38_000,
        integer=True,
    ),
    Question(
        "How many McDonald's restaurants are there in the United States?",
        13_500,
        integer=True,
    ),
    Question(
        "How many licensed drivers are there in the United States?",
        230_000_000,
        integer=True,
    ),
    Question(
        "How many pizza restaurants are there in the United States?",
        75_000,
        integer=True,
    ),
    Question(
        "How many K-12 schools are there in the United States?",
        130_000,
        integer=True,
    ),
    Question(
        "What is the height of Mount Everest in feet?",
        29_032,
        integer=True,
    ),
    Question(
        "What is the average distance from the Earth to the Moon in miles?",
        238_900,
        integer=True,
    ),
    Question(
        "How many seats are in Yankee Stadium?",
        47_000,
        integer=True,
    ),
    Question(
        "How many babies are born in the United States per day?",
        10_000,
        integer=True,
    ),
    Question(
        "How many commercial flight departures are there per day in the United States?",
        28_000,
        integer=True,
    ),
    Question(
        "How many golf courses are there in the United States?",
        16_000,
        integer=True,
    ),
    Question(
        "How many words are in the average adult's vocabulary?",
        30_000,
        integer=True,
    ),
    Question(
        "How many pet dogs are there in the United States?",
        90_000_000,
        integer=True,
    ),
    Question(
        "How many convenience stores are there in the United States?",
        150_000,
        integer=True,
    ),
    Question(
        "What is the population of Canada?",
        41_000_000,
        integer=True,
    ),
    Question(
        "How many bridges are there in New York City?",
        2_000,
        integer=True,
    ),
    Question(
        "How many acres is Central Park?",
        843,
        integer=True,
    ),
    Question(
        "How many tennis balls fit in a standard limousine?",
        60_000,
        integer=True,
    ),
    Question(
        "How many barbershops are there in the United States?",
        100_000,
        integer=True,
    ),
    Question(
        "How many movie tickets are sold in the United States per year?",
        1_200_000_000,
        integer=True,
    ),
]


def random_question() -> Question:
    roll = random.random()
    if roll < 0.60:
        return random.choice(MATH_GENERATORS)()
    if roll < 0.85:
        return random.choice(FERMI_QUESTIONS)
    return random.choice(STATIC_QUESTIONS)


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

Action = str  # "buy" | "sell" | "pass"


@dataclass
class Trade:
    action: Action
    price: float
    belief: float


@dataclass
class RoundState:
    question: Question
    position: float = 0.0
    cash: float = 0.0
    trades: list[Trade] = field(default_factory=list)

    def apply_trade(self, action: Action, price: float, belief: float) -> str:
        if action == "buy":
            # Counterparty buys at your ask — you sell.
            self.position -= 1
            self.cash += price
            side = "SELL"
        elif action == "sell":
            # Counterparty sells at your bid — you buy.
            self.position += 1
            self.cash -= price
            side = "BUY"
        else:
            return ""

        self.trades.append(Trade(action, price, belief))
        return side

    def mark_to_market_pnl(self, true_value: float) -> float:
        return self.cash + self.position * true_value


class RandomBeliefStrategy:
    """Pick a noisy estimate near the true value and trade if it falls outside the spread."""

    def __init__(self, noise_fraction: float = 0.10, min_noise: float = 0.02):
        self.noise_fraction = noise_fraction
        self.min_noise = min_noise

    @property
    def name(self) -> str:
        return "random"

    def reset(self) -> None:
        pass

    def belief(self, question: Question) -> float:
        true = question.true_value
        if question.integer:
            sigma = max(2.0, true * self.noise_fraction)
            return round(true + random.gauss(0, sigma))
        sigma = max(self.min_noise, abs(true) * self.noise_fraction)
        return true + random.gauss(0, sigma)

    def decide(self, bid: float, ask: float, belief: float) -> Action:
        if belief > ask:
            return "buy"
        if belief < bid:
            return "sell"
        return "pass"


@dataclass
class _QuoteRecord:
    bid: float
    ask: float
    action: Action

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2


class ExploitativeStrategy:
    """Knows the true value; picks off misquotes and trades inside tight spreads to bait bad adjustments."""

    def __init__(
        self,
        min_edge_fraction: float = 0.0,
        max_inside_spread: float | None = None,
    ):
        self.min_edge_fraction = min_edge_fraction
        self.max_inside_spread = (
            max_inside_spread
            if max_inside_spread is not None
            else random.uniform(0.05, 0.10)
        )
        self._history: list[_QuoteRecord] = []

    @property
    def name(self) -> str:
        return "exploit"

    def reset(self) -> None:
        self._history.clear()

    def belief(self, question: Question) -> float:
        return question.true_value

    def _record(self, bid: float, ask: float, action: Action) -> Action:
        self._history.append(_QuoteRecord(bid, ask, action))
        return action

    def _spread_too_wide(self, bid: float, ask: float) -> bool:
        spread_pct = _spread_pct_of_midpoint(bid, ask)
        if spread_pct is None:
            return True
        return spread_pct > self.max_inside_spread

    def decide(self, bid: float, ask: float, belief: float) -> Action:
        true = belief
        mid = (bid + ask) / 2
        min_edge = self.min_edge_fraction * max(abs(true), 1e-9)
        inside = bid <= true <= ask

        buy_edge = true - ask   # > 0 when your ask is cheap (you sell low)
        sell_edge = bid - true  # > 0 when your bid is rich (you buy high)

        # Pick off quotes mispriced vs the true value.
        if buy_edge > min_edge and buy_edge >= sell_edge:
            return self._record(bid, ask, "buy")
        if sell_edge > min_edge:
            return self._record(bid, ask, "sell")

        # Wide two-sided market bracketing the truth — stand down.
        if inside and self._spread_too_wide(bid, ask):
            return self._record(bid, ask, "pass")

        # Lean into your adjustments when the spread is tight enough to engage.
        if self._history:
            prev = self._history[-1]
            mid_drop = mid < prev.mid
            mid_rise = mid > prev.mid

            if prev.action == "buy" and mid_drop:
                return self._record(bid, ask, "buy")
            if prev.action == "sell" and mid_rise:
                return self._record(bid, ask, "sell")
            if mid_drop:
                return self._record(bid, ask, "buy")
            if mid_rise:
                return self._record(bid, ask, "sell")

        # True value inside a tight spread: trade to probe and bait movement.
        if inside:
            if true > mid:
                return self._record(bid, ask, "buy")
            if true < mid:
                return self._record(bid, ask, "sell")
            return self._record(bid, ask, "buy")

        return self._record(bid, ask, "pass")


CounterpartyStrategy = RandomBeliefStrategy | ExploitativeStrategy

STRATEGY_CHOICES: dict[str, Callable[[], CounterpartyStrategy]] = {
    "random": RandomBeliefStrategy,
    "exploit": ExploitativeStrategy,
}


def _prompt_strategy(default: str = "exploit") -> CounterpartyStrategy:
    try:
        raw = input(f"Counterparty strategy (random/exploit) [{default}]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return STRATEGY_CHOICES[default]()
    if not raw:
        raw = default
    if raw not in STRATEGY_CHOICES:
        print(f"Unknown strategy, using {default}.")
        raw = default
    return STRATEGY_CHOICES[raw]()


# ---------------------------------------------------------------------------
# Terminal helpers
# ---------------------------------------------------------------------------

def _fmt(value: float, integer: bool = False) -> str:
    if integer:
        return f"{round(value):.0f}"
    return f"{value:.6g}"


def _parse_quote(line: str) -> tuple[float, float] | None:
    parts = line.strip().split()
    if len(parts) != 2:
        return None
    try:
        bid = float(parts[0])
        ask = float(parts[1])
    except ValueError:
        return None
    if bid >= ask:
        return None
    return bid, ask


def _spread_pct_of_midpoint(bid: float, ask: float) -> float | None:
    mid = (bid + ask) / 2
    if abs(mid) < 1e-12:
        return None
    return (ask - bid) / abs(mid)


def _expected_quote_for_midpoint(mid: float, spread_pct: float) -> tuple[float, float]:
    half = abs(mid) * spread_pct / 2
    return mid - half, mid + half


def _validate_fixed_spread(
    bid: float,
    ask: float,
    spread_pct: float,
    *,
    rtol: float = 0.001,
) -> str | None:
    """Return an error message if the quote violates the fixed spread, else None."""
    actual = _spread_pct_of_midpoint(bid, ask)
    mid = (bid + ask) / 2
    if actual is None:
        return (
            "Quote midpoint is too close to zero for a percentage spread. "
            "Center your market away from zero."
        )
    max_spread = spread_pct * (1 + rtol)
    if actual > max_spread:
        exp_bid, exp_ask = _expected_quote_for_midpoint(mid, spread_pct)
        return (
            f"Spread is {actual * 100:.4g}% of midpoint ({_fmt(mid)}); "
            f"max allowed is {spread_pct * 100:g}%. "
            f"Widest valid quote at this midpoint ≈ {_fmt(exp_bid)} / {_fmt(exp_ask)}; "
            f"got {_fmt(bid)} / {_fmt(ask)}."
        )
    return None


def _timed_input(prompt: str, timeout: float) -> str | None:
    """Read a line; prints '5 seconds left' once near the end. Returns None on timeout."""
    if timeout <= 0:
        try:
            return input(prompt).strip()
        except EOFError:
            return None

    if not sys.stdin.isatty():
        try:
            return input(prompt).strip()
        except EOFError:
            return None

    if sys.platform == "win32":
        return _timed_input_windows(prompt, timeout)
    return _timed_input_posix(prompt, timeout)


def _timed_input_posix(prompt: str, timeout: float) -> str | None:
    import select

    deadline = time.monotonic() + timeout
    warned = False

    sys.stdout.write(prompt)
    sys.stdout.flush()

    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                sys.stdout.write("\n")
                sys.stdout.flush()
                return None

            if not warned and remaining <= 5:
                print("5 seconds left")
                warned = True

            ready, _, _ = select.select([sys.stdin], [], [], 0.25)
            if ready:
                line = sys.stdin.readline()
                if not line:
                    return None
                if time.monotonic() > deadline:
                    if line.strip():
                        print("(received after time expired — ignored)")
                    return None
                return line.strip()
    except KeyboardInterrupt:
        print()
        raise


def _timed_input_windows(prompt: str, timeout: float) -> str | None:
    import msvcrt

    deadline = time.monotonic() + timeout
    warned = False
    buf: list[str] = []

    sys.stdout.write(prompt)
    sys.stdout.flush()

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            sys.stdout.write("\n")
            sys.stdout.flush()
            return None

        if not warned and remaining <= 5:
            sys.stdout.write("\n5 seconds left\n")
            sys.stdout.write(prompt + "".join(buf))
            sys.stdout.flush()
            warned = True

        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch == "\x03":  # Ctrl-C
                sys.stdout.write("\n")
                sys.stdout.flush()
                raise KeyboardInterrupt
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                line = "".join(buf).strip()
                if time.monotonic() > deadline:
                    if line:
                        print("(received after time expired — ignored)")
                    return None
                return line
            if ch in ("\x08", "\x7f"):  # Backspace
                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if ch in ("\x00", "\xe0"):
                # Function/arrow key prefix; consume the scancode and ignore.
                msvcrt.getwch()
                continue
            buf.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()
        else:
            time.sleep(0.02)


def _prompt_rounds_per_question(default: int = 6) -> int:
    try:
        raw = input(f"Rounds per question [{default}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    if not raw:
        return default
    try:
        n = int(raw)
        if n < 1:
            raise ValueError
        return n
    except ValueError:
        print(f"Invalid input, using {default}.")
        return default


def _prompt_fixed_spread(default: float = 0.10) -> float | None:
    default_pct = default * 100
    try:
        raw = input(f"Fixed spread % of midpoint [{default_pct:g}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    if not raw:
        return default
    if raw.lower() in {"none", "n"}:
        return None
    raw = raw.rstrip("%").strip()
    try:
        val = float(raw)
        if val <= 0:
            raise ValueError
        return val / 100
    except ValueError:
        print(f"Invalid input, using {default_pct:g}%.")
        return default


def _prompt_time_limit(default: int = 30) -> float:
    try:
        raw = input(f"Time limit per quote in seconds [{default}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return float(default)
    if not raw:
        return float(default)
    if raw.lower() in {"none", "n", "off", "0"}:
        return 0.0
    try:
        val = float(raw)
        if val < 0:
            raise ValueError
        return val
    except ValueError:
        print(f"Invalid input, using {default}.")
        return float(default)


def _print_header(
    rounds_per_question: int,
    fixed_spread: float | None,
    time_limit: float,
    strategy_name: str,
) -> None:
    print()
    print("=" * 60)
    print("  MARKET MAKING GAME")
    print("=" * 60)
    print()
    print("You are the market maker. Quote a bid and ask for each question.")
    print("The counterparty may buy (hit your ask), sell (hit your bid), or pass.")
    print(f"Counterparty strategy: {strategy_name}")
    print(f"Each question runs for {rounds_per_question} rounds; P&L settles at the end.")
    if fixed_spread is not None:
        print(
            f"Fixed max spread: {fixed_spread * 100:g}% of midpoint "
            f"(your spread may be narrower)."
        )
    if time_limit > 0:
        secs = int(time_limit) if time_limit == int(time_limit) else time_limit
        print(f"Time limit: {secs}s per quote (warning at 5 seconds left).")
    print()
    print("Commands:")
    if fixed_spread is None:
        print("  <bid> <ask>   quote prices (bid must be < ask)")
    else:
        print("  <bid> <ask>   quote prices (bid < ask, max spread enforced)")
    print("  status        show position and trade history")
    print("  pass / skip   abandon this question and get a new one (no P&L)")
    print("  quit          exit the game")
    print()


def _print_question_intro(question: Question, rounds_per_question: int) -> None:
    print("-" * 60)
    print(f"Question: {question.prompt}")
    print(f"Quote {rounds_per_question} times; P&L settles after round {rounds_per_question}.")
    print("-" * 60)


def _describe_trade(action: Action, price: float) -> str:
    if action == "buy":
        return (
            f"Counterparty BUYS at your ask of {_fmt(price)} "
            f"(you SELL 1 unit)"
        )
    if action == "sell":
        return (
            f"Counterparty SELLS at your bid of {_fmt(price)} "
            f"(you BUY 1 unit)"
        )
    return "Counterparty PASSES (inside your spread)"


def _print_status(state: RoundState, *, debug: bool = False) -> None:
    pos = state.position
    if pos > 0:
        pos_label = f"long {pos:.0f}"
    elif pos < 0:
        pos_label = f"short {abs(pos):.0f}"
    else:
        pos_label = "flat"
    print(f"Position: {pos_label}  |  Cash: {state.cash:+.6g}")
    if state.trades:
        print("Trades:")
        for i, t in enumerate(state.trades, 1):
            if t.action == "buy":
                label = f"sold @ {_fmt(t.price)}"
            else:
                label = f"bought @ {_fmt(t.price)}"
            belief_note = f"  (belief: {_fmt(t.belief)})" if debug else ""
            print(f"  {i}. Counterparty {t.action} → you {label}{belief_note}")


def _settle_question(
    state: RoundState,
    rounds_per_question: int,
    *,
    debug: bool = False,
) -> float:
    true = state.question.true_value
    pnl = state.mark_to_market_pnl(true)
    integer = state.question.integer

    print()
    print("=" * 60)
    print("QUESTION SETTLED")
    print("=" * 60)
    print(f"Question: {state.question.prompt}")
    print(f"Rounds played: {rounds_per_question}")
    print(f"True value: {_fmt(true, integer)}")
    _print_status(state, debug=debug)
    print()
    print(f"Mark-to-market P&L: {pnl:+.6g}")
    if state.position != 0:
        print(
            f"  (cash {state.cash:+.6g} + position {state.position:.0f}"
            f" × {_fmt(true, integer)})"
        )
        if state.position > 0:
            print("  Long exposure: you gain if the true value is above your avg buy.")
        else:
            print("  Short exposure: you gain if the true value is below your avg sell.")
    print("=" * 60)
    return pnl


def _run_question_session(
    strategy: CounterpartyStrategy,
    question: Question,
    rounds_per_question: int,
    *,
    debug: bool = False,
    fixed_spread: float | None = None,
    time_limit: float = 30,
) -> float | None:
    state = RoundState(question=question)
    strategy.reset()
    _print_question_intro(question, rounds_per_question)

    for round_num in range(1, rounds_per_question + 1):
        print(f"\n--- Round {round_num} of {rounds_per_question} ---")

        while True:
            try:
                line = _timed_input("bid ask> ", time_limit)
            except KeyboardInterrupt:
                print()
                return None

            if line is None:
                print("No quote this round.")
                break

            if not line:
                continue

            lower = line.lower()
            if lower in {"quit", "q", "exit"}:
                return None
            if lower == "status":
                _print_status(state, debug=debug)
                continue
            if lower in {"skip", "pass"}:
                print("Skipping this question (no P&L).\n")
                return 0.0

            quote = _parse_quote(line)
            if quote is None:
                if fixed_spread is None:
                    print("Enter two numbers: bid ask  (bid must be less than ask)")
                else:
                    pct = fixed_spread * 100
                    print(
                        f"Enter two numbers: bid ask  (bid < ask, "
                        f"spread ≤ {pct:g}% of midpoint)"
                    )
                continue

            bid, ask = quote
            if fixed_spread is not None:
                spread_error = _validate_fixed_spread(bid, ask, fixed_spread)
                if spread_error:
                    print(spread_error)
                    continue

            belief = strategy.belief(question)
            action = strategy.decide(bid, ask, belief)

            if debug:
                print(f"  [counterparty belief: {_fmt(belief, question.integer)}]")
            print(f"  {_describe_trade(action, bid if action == 'sell' else ask)}")

            if action != "pass":
                state.apply_trade(action, ask if action == "buy" else bid, belief)

            _print_status(state, debug=debug)
            break

    return _settle_question(state, rounds_per_question, debug=debug)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Market making practice game")
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="show counterparty beliefs after each round",
    )
    parser.add_argument(
        "--spread",
        type=float,
        default=None,
        metavar="PCT",
        help="max allowed spread as %% of midpoint (e.g. 20 for 20%%); skips prompt",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=None,
        metavar="SECS",
        help="seconds per quote (0 to disable); skips prompt",
    )
    parser.add_argument(
        "--strategy",
        choices=sorted(STRATEGY_CHOICES),
        default=None,
        help="counterparty strategy (random or exploit); skips prompt",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    random.seed()
    rounds_per_question = _prompt_rounds_per_question()
    if args.spread is not None:
        if args.spread <= 0:
            print("Spread must be positive; no fixed spread applied.")
            fixed_spread = None
        else:
            fixed_spread = args.spread / 100
    else:
        fixed_spread = _prompt_fixed_spread()
    if args.time_limit is not None:
        time_limit = max(0.0, args.time_limit)
    else:
        time_limit = _prompt_time_limit()
    if args.strategy is not None:
        strategy = STRATEGY_CHOICES[args.strategy]()
    else:
        strategy = _prompt_strategy()
    if isinstance(strategy, ExploitativeStrategy) and fixed_spread is not None:
        strategy.max_inside_spread = random.uniform(0.5, 0.8) * fixed_spread
    _print_header(rounds_per_question, fixed_spread, time_limit, strategy.name)

    session_pnl = 0.0
    questions_played = 0

    try:
        while True:
            question = random_question()
            result = _run_question_session(
                strategy,
                question,
                rounds_per_question,
                debug=args.debug,
                fixed_spread=fixed_spread,
                time_limit=time_limit,
            )

            if result is None:
                break

            session_pnl += result
            questions_played += 1

            print(
                f"Session P&L after {questions_played} question(s): "
                f"{session_pnl:+.6g}"
            )
            print()

            try:
                again = input("Play another question? [Y/n] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if again in {"n", "no", "quit", "q"}:
                break

    except KeyboardInterrupt:
        print("\nInterrupted.")

    if questions_played:
        print()
        print(
            f"Final session P&L: {session_pnl:+.6g} "
            f"over {questions_played} question(s)."
        )
    print("Thanks for playing.")


if __name__ == "__main__":
    main()
