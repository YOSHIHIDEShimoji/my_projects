""""
3 * p**3 - p**2 * q - p * q**2 + 3 * q**3 = 2013
を満たす正の整数p, qの組を全て求めよ。
（一橋大2013）
"""

sol = []

max_value = 1000

for p in range(1, max_value):
    for q in range(1, max_value):
        left_side = 3 * p**3 - p**2 * q - p * q**2 + 3 * q**3
        
        if left_side == 2013:
            sol.append([p, q])

# print(sol)

for p, q in sol:
    print(f'(p, q) = ({p}, {q})')
