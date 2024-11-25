import matplotlib.pyplot as plt

# FIFO Algorithm
def fifo_algorithm(pages, cachesize):
    cache = []
    page_faults = 0

    for page in pages:
        if page not in cache:
            page_faults += 1
            if len(cache) >= cachesize:
                cache.pop(0)  # Видаляємо найстарішу сторінку
            cache.append(page)

    return page_faults

# LRU Algorithm
def lru_algorithm(pages, cachesize):
    cache = []
    page_faults = 0

    for page in pages:
        if page not in cache:
            page_faults += 1
            if len(cache) >= cachesize:
                cache.pop(0)  # Видаляємо найменш недавно використану сторінку
        else:
            cache.remove(page)  # Переміщуємо сторінку в кінець
        cache.append(page)

    return page_faults

# WSClock Algorithm Helper
def wsclock_algorithm(new_page):
    global memory, clock_pointer, ref_bits, access_time, time_now, tau

    start_pointer = clock_pointer  # Для перевірки проходження по всьому колу
    while True:
        candidate_page = memory[clock_pointer]

        # Перевірка біта посилання
        if ref_bits[candidate_page] == 1:
            ref_bits[candidate_page] = 0  # Скидаємо біт посилання
        else:
            # Перевірка часу останнього доступу
            if time_now - access_time[candidate_page] > tau:
                # Заміщуємо сторінку
                del ref_bits[candidate_page]
                del access_time[candidate_page]
                memory[clock_pointer] = new_page
                ref_bits[new_page] = 1
                access_time[new_page] = time_now
                return  # Завершуємо пошук

        # Перехід до наступної сторінки
        clock_pointer = (clock_pointer + 1) % len(memory)

        # Якщо ми повернулися до стартової позиції, заміщуємо сторінку без перевірок
        if clock_pointer == start_pointer:
            victim_page = memory[clock_pointer]
            del ref_bits[victim_page]
            del access_time[victim_page]
            memory[clock_pointer] = new_page
            ref_bits[new_page] = 1
            access_time[new_page] = time_now
            return

# WSClock Simulation
def wsclock_simulation(pages, cachesize):
    global memory, clock_pointer, ref_bits, access_time, time_now, tau
    memory = []
    ref_bits = {}
    access_time = {}
    clock_pointer = 0
    tau = 10  # Час "старіння"
    time_now = 0

    page_faults = 0

    for page in pages:
        time_now += 1  # Оновлюємо час
        if page in memory:
            ref_bits[page] = 1  # Оновлюємо біт посилання
            access_time[page] = time_now
        else:
            page_faults += 1
            if len(memory) >= cachesize:
                wsclock_algorithm(page)
            else:
                memory.append(page)
                ref_bits[page] = 1
                access_time[page] = time_now

    return page_faults

# Main Function for Comparison
if __name__ == "__main__":
    # Дані для тестування
    pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    cache_sizes = range(1, 6)

    # Результати для кожного алгоритму
    fifo_results = [fifo_algorithm(pages, size) for size in cache_sizes]
    lru_results = [lru_algorithm(pages, size) for size in cache_sizes]
    wsclock_results = [wsclock_simulation(pages, size) for size in cache_sizes]

    # Вивід результатів
    print("Кількість відмов сторінок для різних розмірів кешу:")
    print(f"FIFO: {fifo_results}")
    print(f"LRU: {lru_results}")
    print(f"WSClock: {wsclock_results}")

    # Побудова графіка
    plt.plot(cache_sizes, fifo_results, label="FIFO", marker='o')
    plt.plot(cache_sizes, lru_results, label="LRU", marker='s')
    plt.plot(cache_sizes, wsclock_results, label="WSClock", marker='^')
    plt.xlabel("Розмір кешу")
    plt.ylabel("Кількість відмов сторінок")
    plt.legend()
    plt.title("Порівняння алгоритмів заміщення сторінок")
    plt.grid()
    plt.show()
