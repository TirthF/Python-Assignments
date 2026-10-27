"""
Module Dependency Resolver Implementation
"""
import heapq

def main():
    # 1. Read configuration (modules and dependencies)
    while True:
        try:
            line = input("Enter number of modules (n) and dependencies (e): ").strip()
            n, e = map(int, line.split())
            if n < 0 or e < 0:
                print("Error: Values cannot be negative.")
                continue
            break
        except ValueError:
            print("Error: Please enter exactly two integers.")

    modules = []
    graph = {}
    indegree = {}

    # 2. Read module names
    if n > 0:
        print(f"Enter the names of the {n} modules:")
    for i in range(n):
        module = input(f"Module {i+1}: ").strip()
        modules.append(module)
        graph[module] = set()
        indegree[module] = 0

    # 3. Read dependencies
    if e > 0:
        print(f"Enter the {e} dependencies (e.g., 'A B' means A depends on B):")
    for i in range(e):
        while True:
            try:
                line = input(f"Dependency {i+1}: ").strip()
                a, b = line.split()
                if b not in graph[a]:
                    graph[a].add(b)
                    indegree[b] += 1
                break
            except ValueError:
                print("Error: Please enter exactly two module names separated by space.")

    # 4. Perform topological sort using a heap
    heap = []

    for module in modules:
        if indegree[module] == 0:
            heapq.heappush(heap, module)

    order = []

    while heap:
        module = heapq.heappop(heap)
        order.append(module)

        for dependent in sorted(graph[module]):
            indegree[dependent] -= 1

            if indegree[dependent] == 0:
                heapq.heappush(heap, dependent)

    # 5. Output results
    print("\n--- Results ---")
    if len(order) == n:
        print(*order)
    else:
        print("CYCLE")

        # Find and print the cycle path
        state = {module: 0 for module in modules}
        parent = {}
        cycle = []

        def find_cycle(node):
            state[node] = 1

            for neighbor in graph[node]:
                if state[neighbor] == 0:
                    parent[neighbor] = node
                    if find_cycle(neighbor):
                        return True

                elif state[neighbor] == 1:
                    cycle.append(neighbor)

                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent[current]

                    cycle.append(neighbor)
                    cycle.reverse()
                    return True

            state[node] = 2
            return False

        for module in sorted(modules):
            if state[module] == 0:
                if find_cycle(module):
                    break

        print(*cycle)


if __name__ == "__main__":
    main()