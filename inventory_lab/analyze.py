import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .db import DEFAULT_DB, FIRST, LAST, ROOT, connect
from .metrics import checked_tables


def export(db=DEFAULT_DB, out=ROOT / "outputs", as_of=LAST):
    with connect(db) as connection:
        tables = checked_tables(connection, as_of)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(out / f"{name}.csv", encoding="utf-8-sig", index=False)
    lots = tables["lots"]
    stock = lots[lots.on_hand.gt(0)]
    focus = stock[stock.product_id.eq(stock.product_id.min())]
    moves = tables["movements"]
    calendar = pd.date_range(FIRST, as_of).strftime("%Y-%m-%d")
    activity = pd.crosstab(moves.occurred_at.str[:10], moves.kind).reindex(
        index=calendar, columns=["receipt","issue"], fill_value=0)
    sns.set_theme(style="whitegrid")
    charts = [
        ("status","Lô còn tồn theo trạng thái","Số lô",stock,
         lambda ax: stock.status.value_counts().rename(
             index={"valid":"Còn hạn","expiring":"Sắp hết hạn","expired":"Hết hạn"}).plot.bar(ax=ax,rot=0)),
        ("expiry","Lô sắp hết hạn theo ngày","Số lô",tables["expiring"],
         lambda ax: tables["expiring"].expires_on.value_counts().sort_index().plot.bar(ax=ax,rot=25)),
        ("product","Tồn theo lô của mặt hàng có mã nhỏ nhất",
         str(focus.unit.iloc[0]) if len(focus) else "Số lượng",focus,
         lambda ax: sns.barplot(data=focus,x="lot_id",y="on_hand",ax=ax)),
        ("activity","Biến động theo ngày","Số lượt",moves,
         lambda ax: activity.rename(columns={"receipt":"Nhập","issue":"Xuất"}).plot(ax=ax)),
    ]
    for name,title,unit,data,draw in charts:
        fig, ax = plt.subplots(figsize=(9,4.5), layout="constrained")
        if data.empty:
            ax.text(.5,.5,"Chưa có dữ liệu phù hợp",ha="center",transform=ax.transAxes)
            ax.set_axis_off()
        else:
            draw(ax)
            ax.set(ylabel=unit,xlabel="")
        ax.set_title(title)
        fig.savefig(out / f"{name}.png",dpi=140)
        plt.close(fig)

    (out / "report.md").write_text(
        f"# Kho theo lô — dữ liệu giả lập\n\nMốc hết ngày {as_of}, giờ Việt Nam.\n\n"
        f"1. {len(stock)}/{len(lots)} lô đã nhập còn tồn vật lý.\n"
        f"2. {len(tables['expiring'])}/{len(stock)} lô còn tồn hết hạn trong 0–7 ngày.\n"
        f"3. {len(tables['expired'])}/{len(stock)} lô còn tồn đã hết hạn.\n\n"
        "Ngày ghi hạn vẫn đủ điều kiện xuất. Tồn hết hạn chỉ xuất hiện trong tồn vật lý. "
        "Số lượng chỉ cộng trong cùng mặt hàng và đơn vị.\n", encoding="utf-8")
    return tables


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs")
    parser.add_argument("--as-of",default=LAST)
    args = parser.parse_args()
    export(**vars(args))
    print(args.out.resolve())


if __name__ == "__main__":
    main()

