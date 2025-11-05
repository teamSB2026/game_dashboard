import csv
import sys

def generate_random_name(index):
    surnames = ['田中', '佐藤', '鈴木', '高橋', '渡辺', '伊藤', '山本', '中村', '小林', '加藤']
    first_names = ['太郎', '花子', '一郎', '次郎', '美咲', '健太', 'さくら', '大輔', '愛', '翔']
    return f"{surnames[index % len(surnames)]}{first_names[(index // len(surnames)) % len(first_names)]}"

def generate_random_kana(index):
    surnames_kana = ['タナカ', 'サトウ', 'スズキ', 'タカハシ', 'ワタナベ', 'イトウ', 'ヤマモト', 'ナカムラ', 'コバヤシ', 'カトウ']
    first_names_kana = ['タロウ', 'ハナコ', 'イチロウ', 'ジロウ', 'ミサキ', 'ケンタ', 'サクラ', 'ダイスケ', 'アイ', 'ショウ']
    return f"{surnames_kana[index % len(surnames_kana)]}{first_names_kana[(index // len(surnames_kana)) % len(first_names_kana)]}"

def generate_random_email(index):
    return f"user{str(index + 1).zfill(3)}@example.com"

def anonymize_csv(input_path, output_path):
    with open(input_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    anonymized = []
    for i, row in enumerate(rows):
        new_row = row.copy()

        if "メールアドレス" in row:
            new_row["メールアドレス"] = generate_random_email(i)

        if "お名前(漢字)" in row:
            new_row["お名前(漢字)"] = generate_random_name(i)

        if "お名前(フリガナ)" in row:
            new_row["お名前(フリガナ)"] = generate_random_kana(i)

        anonymized.append(new_row)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=anonymized[0].keys())
        writer.writeheader()
        writer.writerows(anonymized)

    print(f"✅ {len(anonymized)} 件のレコードを匿名化しました。")
    print(f"📄 出力ファイル: {output_path}")

if __name__ == "__main__":

    input_path = "data/名簿一覧_id.csv"
    output_path = "data/名簿一覧_id_匿名化.csv"
    anonymize_csv(input_path, output_path)
