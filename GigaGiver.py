import os
import random

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    try:
        size_mb = float(input("What size do you want (in Mb)? "))
        if size_mb <= 0:
            print("Size would be >0.")
            return
    except ValueError:
        print("For example: 5")
        return

    file_path = os.path.join(folder, "Just a file")
    bytes_per_chunk = 1024 * 1024  # 1 МБ
    remaining = int(size_mb * 1024 * 1024)

    with open(file_path, "wb") as f:
        while remaining > 0:
            chunk_size = min(bytes_per_chunk, remaining)
            f.write(b"\x00" * chunk_size)
            remaining -= chunk_size

    print(f"Готово! Файл: {file_path}")
    print(f"Размер: {os.path.getsize(file_path) / (1024 * 1024):.2f} МБ")

if __name__ == "__main__":
    main()
