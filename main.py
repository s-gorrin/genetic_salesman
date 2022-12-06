from TOrder import TOrder

# sm = TOrder('assignment_cities.csv')
sm = TOrder('cities.csv')

route, path, distance = sm.run(100)
print(f"relative route {route}")
print(f"absolute path: {sm.path_string(path)}")
print(f"distance {distance}")
print("\nRunning longer test...")
results = {}
for i in range(10):
    route, path, distance = sm.run(500)
    results[distance] = [route, path]

best = min(results.keys())
print(sm.path_string(results[best][1]))
print(f"relative: {results[best][0]}")
print(f"distance: {best} miles")
