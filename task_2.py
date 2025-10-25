import json
import time
import mmh3
from datasketch import HyperLogLog
import math

def load_ip_addresses(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # Parse JSON line
                log_entry = json.loads(line)

                # Extract remote_addr field
                if 'remote_addr' in log_entry:
                    ip_address = log_entry['remote_addr']
                    if ip_address:
                        yield ip_address

            except json.JSONDecodeError:
                continue
            except Exception:
                continue


def exact_count_unique(file_path):
    start_time = time.time()

    unique_ips = set()
    for ip in load_ip_addresses(file_path):
        unique_ips.add(ip)

    end_time = time.time()
    execution_time = end_time - start_time

    return len(unique_ips), execution_time


def hyperloglog_count_unique(file_path, precision=14):
    start_time = time.time()

    hll = HyperLogLog(p=precision)
    i = 0
    for ip in load_ip_addresses(file_path):
        i= i + 1
        hll.update(ip.encode('utf-8'))

    print(i)

    estimated_count = hll.count()

    end_time = time.time()
    execution_time = end_time - start_time

    return estimated_count, execution_time


def print_comparison_table(exact_count, exact_time, hll_count, hll_time):
    error_percentage = abs(exact_count - hll_count) / exact_count * 100

    print("\nРезультати порівняння:")
    print(f"{'':30} {'Точний підрахунок':>20} {'HyperLogLog':>20}")
    print(f"{'Унікальні елементи':30} {exact_count:>20.4f} {hll_count:>20.4f}")
    print(f"{'Час виконання (сек.)':30} {exact_time:>20.4f} {hll_time:>20.4f}")
    print(f"\nПохибка HyperLogLog: {error_percentage:.2f}%")
    print(f"Прискорення: {exact_time/hll_time:.2f}x")


def main():
    log_file_path = "lms-stage-access.log"

    print("Порівняння методів підрахунку унікальних IP-адрес")
    print("=" * 70)

    print("\nВиконується точний підрахунок...")
    exact_count, exact_time = exact_count_unique(log_file_path)
    print(f"Знайдено унікальних IP: {exact_count}")
    print(f"Час виконання: {exact_time:.2f} сек.")

    print("\nВиконується HyperLogLog підрахунок...")
    hll_count, hll_time = hyperloglog_count_unique(log_file_path, precision=14)
    print(f"Оцінка унікальних IP: {hll_count:.0f}")
    print(f"Час виконання: {hll_time:.2f} сек.")

    # Print comparison table
    print_comparison_table(exact_count, exact_time, hll_count, hll_time)


if __name__ == "__main__":
    main()
