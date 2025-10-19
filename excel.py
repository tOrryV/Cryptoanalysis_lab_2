import pandas as pd


def _flatten_cipher(cipher_dict):
    """
    Flatten a nested cipher metrics dictionary into a pandas DataFrame with columns
    [L, Criteria, l, FP, FN], suitable for tabular representation and export.

    :param cipher_dict: dict
        Nested mapping of cipher results:
        {criteria_key: {L: {"alpha": FP, "beta": FN}, ...}, ...}.
        Keys must follow the pattern "criteria_x_y_sym" or "criteria_x_y_bigram".
    :return: pandas.DataFrame
        DF with columns ["L", "Criteria", "l", "FP", "FN"],
        sorted by L, Criteria, and l.
    """

    rows = []
    for crit_key, sizes in cipher_dict.items():
        parts = crit_key.split('_')
        if len(parts) < 4 or parts[0] != "criteria":
            continue
        criteria = f"{parts[1]}.{parts[2]}"
        gram = parts[3]
        lstr = "l=1" if gram == "sym" else "l=2"
        for L, vals in sizes.items():
            rows.append({
                "L": int(L),
                "Criteria": criteria,
                "l": lstr,
                "FP": vals.get("alpha"),
                "FN": vals.get("beta"),
            })
    if not rows:
        return pd.DataFrame(columns=["L", "Criteria", "l", "FP", "FN"])
    return pd.DataFrame(rows).sort_values(["L", "Criteria", "l"]).reset_index(drop=True)


def _pivot_df(df):
    """
    Convert a flat DataFrame with FP/FN values into a pivoted format suitable for Excel export,
    splitting metrics by `l=1` and `l=2`.

    :param df: pandas.DataFrame
        Input DataFrame with columns ["L", "Criteria", "l", "FP", "FN"].
    :return: pandas.DataFrame
        Pivoted DataFrame with columns:
        ["L", "Criteria", "FP (l=1)", "FN (l=1)", "FP (l=2)", "FN (l=2)"].
    """

    fp = df.pivot_table(index=["L", "Criteria"], columns="l", values="FP", aggfunc="first")
    fn = df.pivot_table(index=["L", "Criteria"], columns="l", values="FN", aggfunc="first")
    for col in ["l=1", "l=2"]:
        if col not in fp.columns:
            fp[col] = None
        if col not in fn.columns:
            fn[col] = None
    return pd.DataFrame({
        "L": fp.index.get_level_values("L"),
        "Criteria": fp.index.get_level_values("Criteria"),
        "FP (l=1)": fp["l=1"].values,
        "FN (l=1)": fn["l=1"].values,
        "FP (l=2)": fp["l=2"].values,
        "FN (l=2)": fn["l=2"].values,
    })


def generate_excel(results, output_path):
    """
    Generate a formatted Excel report summarizing cipher detection results for multiple ciphers.

    :param results: dict
        Mapping {cipher_name: cipher_block}, where each cipher_block is a nested dictionary
        of criteria and values suitable for _flatten_cipher().
    :param output_path: str | Path
        File path for the generated Excel file.
    :return: None
        Writes formatted Excel sheets (one per cipher) with merged headers, adjusted column widths,
        and grouped rows by text length L.
    """

    pretty_names = {
        "vigenere_k1": "Sequence by Vigenere cipher (key length: 1)",
        "vigenere_k5": "Sequence by Vigenere cipher (key length: 5)",
        "vigenere_k10": "Sequence by Vigenere cipher (key length: 10)",
        "affine": "Sequence by Affine cipher",
        "affine_bigram": "Sequence by Affine Bigram cipher",
        "random": "Random sequence",
        "recursive": "Recursive sequence",
    }

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        wb = writer.book
        fmt_title = wb.add_format({"bold": True, "align": "center", "valign": "vcenter",
                                   "font_size": 14, "bg_color": "#DCE6F1", "border": 1})
        fmt_head = wb.add_format({"bold": True, "align": "center", "valign": "vcenter",
                                  "bg_color": "#E0E0E0", "border": 1})
        fmt_cell = wb.add_format({"align": "center", "valign": "vcenter", "border": 1})

        for cipher_name, cipher_block in results.items():
            df = _flatten_cipher(cipher_block)
            if df.empty:
                continue
            table = _pivot_df(df)

            ws = wb.add_worksheet(cipher_name)
            writer.sheets[cipher_name] = ws

            title = pretty_names.get(cipher_name, cipher_name)
            ws.merge_range(0, 0, 0, 5, title, fmt_title)

            ws.merge_range(1, 0, 2, 0, "L", fmt_head)
            ws.merge_range(1, 1, 2, 1, "Criteria", fmt_head)
            ws.merge_range(1, 2, 1, 3, "l=1", fmt_head)
            ws.merge_range(1, 4, 1, 5, "l=2", fmt_head)
            ws.write(2, 2, "FP", fmt_head)
            ws.write(2, 3, "FN", fmt_head)
            ws.write(2, 4, "FP", fmt_head)
            ws.write(2, 5, "FN", fmt_head)

            start_row = 3
            for r, row in enumerate(table.itertuples(index=False)):
                for c, val in enumerate(row):
                    ws.write(start_row + r, c, val, fmt_cell)

            headers = ["L", "Criteria", "FP (l=1)", "FN (l=1)", "FP (l=2)", "FN (l=2)"]
            min_widths = [8, 14, 8, 8, 8, 8]
            max_width = 30

            col_widths = [len(h) for h in headers]
            for r in table.itertuples(index=False):
                for c, val in enumerate(r):
                    col_widths[c] = max(col_widths[c], len(str(val)))
            for c, w in enumerate(col_widths):
                ws.set_column(c, c, min(max(w + 2, min_widths[c]), max_width))

            l_vals = table["L"].tolist()
            grp_start = start_row
            for i in range(1, len(l_vals)):
                if l_vals[i] != l_vals[i - 1]:
                    if grp_start != start_row + i - 1:
                        ws.merge_range(grp_start, 0, start_row + i - 1, 0, l_vals[i - 1], fmt_cell)
                    grp_start = start_row + i
            if l_vals and grp_start != start_row + len(l_vals) - 1:
                ws.merge_range(grp_start, 0, start_row + len(l_vals) - 1, 0, l_vals[-1], fmt_cell)

    print(f"Excel file created successfully: {output_path}")
