import pandas as pd
import random
from collections import defaultdict

def parse_company_name(company_full):
    """会社名を略称に変換"""
    if 'ソニーセミコンダクタソリューションズ' in company_full or company_full == 'SSS':
        return 'SSS'
    elif 'ソニーグループ' in company_full or company_full == 'SGC':
        return 'SGC'
    elif 'ソニー・インタラクティブエンタテインメント' in company_full or company_full == 'SIE':
        return 'SIE'
    elif 'ソニー株式会社' in company_full or company_full == 'SEC':
        return 'SEC'
    elif 'その他' in company_full or 'まだ決まってない' in company_full:
        return '未定'
    else:
        return '未定'

def create_member_id(row, company_counts):
    """メンバーIDを作成（例: SEC_社員_0001）"""
    company = row['company_abbr']
    status = row['内定者/社員']
    
    # 会社ごと、社員/内定者ごとのカウントを管理
    key = f"{company}_{status}"
    company_counts[key] += 1
    count = company_counts[key]
    
    return f"{company}_{status}_{count:04d}"

def assign_r1_teams(participants_df):
    """R1ラウンドの班分け（異なる会社を混ぜる）"""
    # 社員と内定者を分ける
    employees = participants_df[participants_df['内定者/社員'] == '社員'].copy()
    candidates = participants_df[participants_df['内定者/社員'] == '内定者'].copy()
    
    # 各会社ごとにシャッフル
    employees = employees.sample(frac=1, random_state=42).reset_index(drop=True)
    candidates = candidates.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # 会社ごとにグループ化
    employees_by_company = {company: group.reset_index(drop=True) 
                           for company, group in employees.groupby('company_abbr')}
    candidates_by_company = {company: group.reset_index(drop=True) 
                            for company, group in candidates.groupby('company_abbr')}
    
    r1_teams = []
    team_id = 1
    
    # 各社の社員と内定者のインデックスを追跡
    emp_indices = {company: 0 for company in employees_by_company}
    cand_indices = {company: 0 for company in candidates_by_company}
    
    # 優先順位: 社員がいる会社から順に班を作る
    companies_with_employees = list(employees_by_company.keys())
    
    # 社員を持つ班を作成
    for company in companies_with_employees:
        while emp_indices[company] < len(employees_by_company[company]):
            team = {}
            team['班ID'] = f'R1-{team_id:02d}'
            team['社員'] = 1
            team['members'] = []
            
            # 社員を追加
            if emp_indices[company] < len(employees_by_company[company]):
                team['members'].append(employees_by_company[company].iloc[emp_indices[company]]['member_id'])
                emp_indices[company] += 1
            
            # 内定者を5名追加（できるだけ異なる会社から）
            # 戦略: 主要会社から2名ずつ、残りは少数会社から
            added_count = 0
            
            # まず現在の社員の会社から内定者を2名追加
            for _ in range(2):
                if cand_indices.get(company, 0) < len(candidates_by_company.get(company, [])):
                    team['members'].append(candidates_by_company[company].iloc[cand_indices[company]]['member_id'])
                    cand_indices[company] += 1
                    added_count += 1
            
            # 他の会社から追加
            other_companies = [c for c in candidates_by_company.keys() if c != company]
            random.shuffle(other_companies)
            
            for other_company in other_companies:
                if added_count >= 5:
                    break
                if cand_indices.get(other_company, 0) < len(candidates_by_company.get(other_company, [])):
                    num_to_add = min(2, 5 - added_count)
                    for _ in range(num_to_add):
                        if cand_indices[other_company] < len(candidates_by_company[other_company]):
                            team['members'].append(candidates_by_company[other_company].iloc[cand_indices[other_company]]['member_id'])
                            cand_indices[other_company] += 1
                            added_count += 1
                            if added_count >= 5:
                                break
            
            if added_count >= 5:
                r1_teams.append(team)
                team_id += 1
    
    # 社員がいない班（内定者のみ）
    # 残った内定者を使って班を作成
    remaining_candidates = []
    for company in candidates_by_company:
        while cand_indices.get(company, 0) < len(candidates_by_company[company]):
            remaining_candidates.append(candidates_by_company[company].iloc[cand_indices[company]])
            cand_indices[company] += 1
    
    # 6人ずつの班を作成
    for i in range(0, len(remaining_candidates), 6):
        if i + 6 <= len(remaining_candidates):
            team = {}
            team['班ID'] = f'R1-{team_id:02d}'
            team['社員'] = 0
            team['members'] = [remaining_candidates[j]['member_id'] for j in range(i, i + 6)]
            r1_teams.append(team)
            team_id += 1
    
    return r1_teams

def assign_r2_teams(participants_df):
    """R2ラウンドの班分け（同じ会社ごと）"""
    r2_teams = []
    
    # 会社ごとにグループ化
    for company, group in participants_df.groupby('company_abbr'):
        group = group.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # 社員を先に配置
        employees = group[group['内定者/社員'] == '社員'].reset_index(drop=True)
        candidates = group[group['内定者/社員'] == '内定者'].reset_index(drop=True)
        
        team_count = 1
        
        # 社員がいる班を作成（社員1名+内定者6名）
        for i in range(len(employees)):
            team = {}
            team['班ID'] = f'R2-{company}{team_count}'
            team['会社'] = company
            team['members'] = [employees.iloc[i]['member_id']]
            
            # 内定者を追加
            start_idx = i * 6
            end_idx = min(start_idx + 6, len(candidates))
            for j in range(start_idx, end_idx):
                team['members'].append(candidates.iloc[j]['member_id'])
            
            r2_teams.append(team)
            team_count += 1
        
        # 残った内定者のみの班を作成
        remaining_start = len(employees) * 6
        for i in range(remaining_start, len(candidates), 6):
            team = {}
            team['班ID'] = f'R2-{company}{team_count}'
            team['会社'] = company
            team['members'] = []
            
            end_idx = min(i + 6, len(candidates))
            for j in range(i, end_idx):
                team['members'].append(candidates.iloc[j]['member_id'])
            
            r2_teams.append(team)
            team_count += 1
    
    return r2_teams

def create_r1_output_df(r1_teams, participants_df):
    """R1班分け結果をDataFrameに変換（名前付き）"""
    # member_idから名前を引けるようにマッピング作成
    id_to_name = dict(zip(participants_df['member_id'], participants_df['お名前(漢字)']))
    
    rows = []
    for team in r1_teams:
        row = {
            '班ID (R1)': team['班ID'],
            '社員': team['社員']
        }
        for i in range(6):
            if i < len(team['members']):
                member_id = team['members'][i]
                member_name = id_to_name.get(member_id, '')
                row[f'メンバー{i+1}'] = f"{member_id} ({member_name})"
            else:
                row[f'メンバー{i+1}'] = ''
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # 各会社の人数をカウント
    company_list = ['SEC', 'SGC', 'SSS', 'SIE', '未定']
    for company in company_list:
        df[company] = df[[f'メンバー{i+1}' for i in range(6)]].apply(
            lambda x: sum(1 for v in x if company in str(v)), axis=1
        )
    
    # 会社数をカウント
    df['会社数'] = df[company_list].apply(lambda x: sum(1 for v in x if v > 0), axis=1)
    
    return df

def create_r2_output_df(r2_teams, participants_df):
    """R2班分け結果をDataFrameに変換（名前付き）"""
    # member_idから名前を引けるようにマッピング作成
    id_to_name = dict(zip(participants_df['member_id'], participants_df['お名前(漢字)']))
    
    rows = []
    for team in r2_teams:
        row = {
            '班ID (R2)': team['班ID'],
            '会社': team['会社']
        }
        for i in range(7):
            if i < len(team['members']):
                member_id = team['members'][i]
                member_name = id_to_name.get(member_id, '')
                row[f'メンバー{i+1}'] = f"{member_id} ({member_name})"
            else:
                row[f'メンバー{i+1}'] = ''
        rows.append(row)
    
    return pd.DataFrame(rows)

def main():
    # CSVファイルを読み込む
    roster_df = pd.read_csv('/mnt/user-data/uploads/名簿一覧_id_匿名化.csv', encoding='utf-8-sig')
    
    # 参加者のみをフィルタリング
    participants = roster_df[roster_df['Bridge2026の参加可否'] == '参加'].copy()
    
    print(f"参加者数: {len(participants)}名")
    
    # 会社名を略称に変換
    participants['company_abbr'] = participants['所属会社(内定先会社)'].apply(parse_company_name)
    
    # 会社ごとの人数を表示
    print("\n会社別参加者数:")
    print(participants.groupby(['company_abbr', '内定者/社員']).size())
    
    # メンバーIDを作成
    company_counts = defaultdict(int)
    participants['member_id'] = participants.apply(
        lambda row: create_member_id(row, company_counts), axis=1
    )
    
    # R1班分け
    print("\n\nR1班分けを実行中...")
    r1_teams = assign_r1_teams(participants)
    r1_df = create_r1_output_df(r1_teams, participants)
    
    # R2班分け
    print("R2班分けを実行中...")
    r2_teams = assign_r2_teams(participants)
    r2_df = create_r2_output_df(r2_teams, participants)
    
    # 結果を結合して出力
    print("\n班分け完了！")
    print(f"R1: {len(r1_teams)}班")
    print(f"R2: {len(r2_teams)}班")
    
    # 出力ファイルを作成
    with pd.ExcelWriter('/mnt/user-data/outputs/班分け結果.xlsx', engine='openpyxl') as writer:
        # R1シート
        r1_df.to_excel(writer, sheet_name='R1', index=False)
        # R2シート
        r2_df.to_excel(writer, sheet_name='R2', index=False)
        # 参加者リスト
        output_participants = participants[['Bridge ID', 'お名前(漢字)', '内定者/社員', 
                                           'company_abbr', 'member_id']].copy()
        output_participants.to_excel(writer, sheet_name='参加者一覧', index=False)
    
    print("\n結果を 班分け結果.xlsx に保存しました")
    
    # CSVでも出力
    r1_df.to_csv('/mnt/user-data/outputs/R1_班分け結果.csv', index=False, encoding='utf-8-sig')
    r2_df.to_csv('/mnt/user-data/outputs/R2_班分け結果.csv', index=False, encoding='utf-8-sig')
    
    return r1_df, r2_df, participants

if __name__ == "__main__":
    r1_df, r2_df, participants_df = main()