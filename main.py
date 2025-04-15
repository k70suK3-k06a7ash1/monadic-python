from maybe_monad import Maybe
# --- サンプルコード ---

print("--- 1. 基本的な使い方 ---")
maybe_int: Maybe[int] = Maybe.just(100)
maybe_str: Maybe[str] = Maybe.just("Hello")
maybe_nothing: Maybe[float] = Maybe.nothing()

print(f"maybe_int: {maybe_int}")
print(f"maybe_str: {maybe_str}")
print(f"maybe_nothing: {maybe_nothing}")

print(f"Is maybe_int Just? {maybe_int.is_just()}")     # True
print(f"Is maybe_int Nothing? {maybe_int.is_nothing()}")  # False
print(f"Is maybe_nothing Just? {maybe_nothing.is_just()}")    # False
print(f"Is maybe_nothing Nothing? {maybe_nothing.is_nothing()}") # True

# __bool__ のおかげでif文で直接使える
if maybe_int:
    print("maybe_int contains a value.")
else:
    print("maybe_int is Nothing.") # こちらは実行されない

if maybe_nothing:
    print("maybe_nothing contains a value.") # こちらは実行されない
else:
    print("maybe_nothing is Nothing.")

# Just(None) は ValueError を発生させる
try:
    Maybe.just(None)
except ValueError as e:
    print(f"Caught expected error for Just(None): {e}")

print("\n--- 2. map の使用 (値の変換) ---")
# Just の中の値を変換する
add_ten = lambda x: x + 10
result_map1 = maybe_int.map(add_ten)
print(f"map(add_10) on {maybe_int}: {result_map1}") # Just(110)

# Nothing に map を適用しても Nothing のまま
result_map2 = maybe_nothing.map(lambda x: x * 2) # この関数は実行されない
print(f"map(x * 2) on {maybe_nothing}: {result_map2}") # Nothing

# map の関数が None を返す場合 -> Nothing になる
result_map_none = maybe_int.map(lambda x: None)
print(f"map(lambda x: None) on {maybe_int}: {result_map_none}") # Nothing (Warningが出るはず)

# map の関数が例外を発生させる場合 -> Nothing になる
def map_with_exception(x):
    return x / 0 # ZeroDivisionError

result_map_ex = maybe_int.map(map_with_exception)
print(f"map(division_by_zero) on {maybe_int}: {result_map_ex}") # Nothing (Warningが出るはず)


print("\n--- 3. bind の使用 (Maybeを返す関数との連携) ---")
# 数値を文字列に変換するが、負の場合は Nothing を返す関数
def int_to_positive_str(n: int) -> Maybe[str]:
    if n >= 0:
        return Maybe.just(f"Number: {n}")
    else:
        return Maybe.nothing()

result_bind1 = maybe_int.bind(int_to_positive_str)
print(f"bind(int_to_positive_str) on {maybe_int}: {result_bind1}") # Just("Number: 100")

maybe_negative_int = Maybe.just(-5)
result_bind2 = maybe_negative_int.bind(int_to_positive_str)
print(f"bind(int_to_positive_str) on {maybe_negative_int}: {result_bind2}") # Nothing

# Nothing に bind を適用しても Nothing のまま
result_bind3 = maybe_nothing.bind(int_to_positive_str) # この関数は実行されない
print(f"bind(int_to_positive_str) on {maybe_nothing}: {result_bind3}") # Nothing

# bind に渡す関数が Maybe を返さない場合 -> TypeError が発生し、捕捉されて Nothing になる
def non_maybe_returning_func(x):
    return x * 2 # Maybeインスタンスではない

result_bind_type_error = maybe_int.bind(non_maybe_returning_func)
print(f"bind(non_maybe_returning_func) on {maybe_int}: {result_bind_type_error}") # Nothing (Warning/TypeErrorが出るはず)

# bind に渡す関数が例外を発生させる場合 -> Nothing になる
def bind_with_exception(x):
    raise ValueError("Something wrong inside bind")

result_bind_ex = maybe_int.bind(bind_with_exception)
print(f"bind(bind_with_exception) on {maybe_int}: {result_bind_ex}") # Nothing (Warningが出るはず)


print("\n--- 4. get_or_else の使用 (デフォルト値の取得) ---")
value1 = maybe_int.get_or_else(0)
print(f"get_or_else(0) from {maybe_int}: {value1}") # 100

value2 = maybe_nothing.get_or_else(0.0)
print(f"get_or_else(0.0) from {maybe_nothing}: {value2}") # 0.0


print("\n--- 5. get_or_raise の使用 (値がない場合に例外) ---")
try:
    value_raise1 = maybe_int.get_or_raise()
    print(f"get_or_raise() from {maybe_int}: {value_raise1}") # 100
except Exception as e:
    print(f"Unexpected error for maybe_int: {e}")

try:
    # カスタム例外を指定
    maybe_nothing.get_or_raise(RuntimeError("Value is absolutely required!"))
except RuntimeError as e:
    print(f"Caught expected error from get_or_raise() on {maybe_nothing}: {e}")
except Exception as e:
    print(f"Caught unexpected error type for maybe_nothing: {e}")


print("\n--- 6. __or__ (or else) の使用 (代替Maybeの提供) ---")
option_a = Maybe.nothing()
option_b = Maybe.just("Use this instead")
option_c = Maybe.just(999)

result_or1 = option_a | option_b
print(f"{option_a} | {option_b}: {result_or1}") # Just("Use this instead")

result_or2 = maybe_int | option_c # maybe_int is Just(100)
print(f"{maybe_int} | {option_c}: {result_or2}") # Just(100)

result_or3 = option_a | Maybe.nothing()
print(f"{option_a} | {Maybe.nothing()}: {result_or3}") # Nothing


print("\n--- 7. メソッドチェーン (連続処理) ---")

# 例: 設定ファイルから読み取った文字列を処理するシナリオ
settings = {"port": " 8080 ", "host": "localhost", "timeout": " abc "}

def get_setting(key: str) -> Maybe[str]:
    # 設定が存在すれば Just(value), なければ Nothing を返す
    value = settings.get(key)
    return Maybe.just(value) if value is not None else Maybe.nothing()

def parse_int(s: str) -> Maybe[int]:
    # 文字列を整数にパース。失敗したら Nothing
    try:
        # strip() で前後の空白を除去
        return Maybe.just(int(s.strip()))
    except (ValueError, TypeError):
        return Maybe.nothing()

def validate_port(port: int) -> Maybe[int]:
    # ポート番号が有効範囲内かチェック
    if 0 < port < 65536:
        return Maybe.just(port)
    else:
        print(f"Warning: Invalid port number {port}")
        return Maybe.nothing()

# ポート番号を取得し、パースし、検証するチェーン
port_setting: Maybe[str] = get_setting("port")
valid_port: Maybe[int] = (
    port_setting          # Maybe[str] or Nothing
    .bind(parse_int)      # Maybe[int] or Nothing
    .bind(validate_port)  # Maybe[int] or Nothing
)
print(f"Result for 'port': {valid_port}") # Just(8080)
print(f"Port number or default: {valid_port.get_or_else(80)}") # 8080

# 存在しないキー "user"
user_setting = get_setting("user")
valid_user = user_setting.bind(parse_int) # 最初のget_settingでNothingなので以降はスキップ
print(f"Result for 'user': {valid_user}") # Nothing
print(f"User ID or default: {valid_user.get_or_else(-1)}") # -1

# パースに失敗するキー "timeout"
timeout_setting = get_setting("timeout")
valid_timeout = (
    timeout_setting       # Just(" abc ")
    .bind(parse_int)      # -> Nothing (parse_intで失敗)
    .map(lambda t: t * 1000) # スキップされる
)
print(f"Result for 'timeout': {valid_timeout}") # Nothing
print(f"Timeout ms or default: {valid_timeout.get_or_else(5000)}") # 5000

print("\n--- 8. 等価比較 ---")
m1 = Maybe.just(10)
m2 = Maybe.just(10)
m3 = Maybe.just(20)
n1 = Maybe.nothing()
n2 = Maybe.nothing()

print(f"{m1} == {m2}: {m1 == m2}") # True
print(f"{m1} == {m3}: {m1 == m3}") # False
print(f"{m1} == {n1}: {m1 == n1}") # False
print(f"{n1} == {n2}: {n1 == n2}") # True
print(f"{m1} != {n1}: {m1 != n1}") # True