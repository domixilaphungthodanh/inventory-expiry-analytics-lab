import argparse
from pathlib import Path

from .db import DEFAULT_DB, LAST, connect
from .metrics import verify_allocation
from .sql_metrics import sql_tables


def show(table):
    if table.empty:
        print("Không có kết quả")
    for offset in range(0, len(table), 20):
        if offset and input("Enter để tiếp tục, q để quay lại: ").strip().lower() == "q":
            break
        print(table.iloc[offset:offset+20].to_string(index=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    with connect(args.db) as connection:
        while True:
            print("\n1. Tìm mặt hàng  2. Tồn theo lô  3. Lịch sử lô")
            print("4. Cảnh báo hạn  5. Mô phỏng FEFO  6. Xuất báo cáo  0. Thoát")
            try:
                choice = input("Chọn số: ").strip()
                if choice in {"0","q"}:
                    return
                if choice not in {"1","2","3","4","5","6"}:
                    print("Chọn số trong menu")
                    continue
                as_of = input(f"Ngày quan sát [{LAST}], q để quay lại: ").strip() or LAST
                if as_of == "q":
                    continue
                tables = sql_tables(connection, as_of)
                if choice == "1":
                    keyword = input("Tên hoặc mã mặt hàng: ").strip()
                    products = tables["products"]
                    show(products[products.name.str.contains(keyword,case=False,regex=False) |
                                  products.product_id.astype(str).eq(keyword)])
                elif choice == "2":
                    show(tables["lots"])
                elif choice == "3":
                    lot = input("Mã lô: ").strip().upper()
                    show(tables["movements"][tables["movements"].lot_id.eq(lot)])
                elif choice == "4":
                    print("Sắp hết hạn")
                    show(tables["expiring"])
                    print("Hết hạn còn tồn")
                    show(tables["expired"])
                elif choice == "5":
                    show(tables["products"][["product_id","name","unit"]])
                    product = int(input("Mã mặt hàng: "))
                    quantity = int(input("Số lượng cần xuất: "))
                    rows, shortage = verify_allocation(connection,tables["lots"],product,quantity,as_of)
                    show(rows)
                    unit = tables["products"].set_index("product_id").loc[product,"unit"]
                    print(f"Mô phỏng lấy {quantity-shortage} {unit}, thiếu {shortage} {unit}.")
                else:
                    from .analyze import export
                    export(args.db, as_of=as_of)
                    print("Đã xuất vào outputs")
            except ValueError as exc:
                print(exc)
            except (EOFError, KeyboardInterrupt):
                return


if __name__ == "__main__":
    main()

