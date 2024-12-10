"""
    要给每张coupon附一个独一无二的UID，基于以下几个前提：
    1. 每种coupon（由COUPON_UPC唯一确定）属于哪一个campaign已知（由表coupon）
    2. 每个campaign发给了哪个household已知（由表campaign_table）
    3. 假设每次household均收到了campaign中包含的所有券（这个假设在campaign属于Type A/ Type B时成立，需要表campaign_desc进行初筛）
    4. UPC唯一属于一种campaign，每个household也只收到过一次campaign
"""

import pandas as pd


def couponUID_generate(coupon: str, campaign_desc: str, campaign_table: str):
    """
    :param coupon: 表coupon的路径
    :param campaign_desc: 表campaign_desc的路径
    :param campaign_table: 表campaign_table的路径
    :return:
    """
    df_coupon = pd.read_csv(coupon)
    df_campaign_desc = pd.read_csv(campaign_desc)
    df_campaign_table = pd.read_csv(campaign_table)
    # 筛选符合条件的campaign name list
    campaign_list = df_campaign_desc[df_campaign_desc['DESCRIPTION'].isin(['TypeA', 'TypeB'])]['CAMPAIGN'].tolist()
    # 由df_coupon生成campaign_bundle
    campaign_bundle = df_coupon.groupby('CAMPAIGN')['COUPON_UPC'].apply(set).apply(list).to_dict()
    campaign_bundle = {k: v for k, v in campaign_bundle.items() if k in campaign_list}
    # 基于campaign_table生成household_bundle
    household_bundle = df_campaign_table.groupby('household_key')['CAMPAIGN'].apply(list).to_dict()
    # 结合上面两个bundle生成UID_bundle
    UID_bundle = {}
    for key, value in household_bundle.items():
        temp = {}
        for campaign in value:
            if campaign not in campaign_bundle:
                continue
            temp[campaign] = campaign_bundle[campaign]
        UID_bundle[key] = temp
    df_UID = pd.DataFrame(
        {'household_key': household_key, 'CAMPAIGN': campaign, 'COUPON_UPC': coupon}
        for household_key, campaign_bundle in UID_bundle.items()
        for campaign, coupons in campaign_bundle.items()
        for coupon in coupons
    )
    # 通过index生成UID
    df_UID['COUPON_UID'] = df_UID.index + 1
    # 将UID移到第一列
    df_UID = df_UID[['COUPON_UID', 'household_key', 'CAMPAIGN', 'COUPON_UPC']]
    # 保存
    df_UID.to_csv('../data/coupon_UID.csv', index=False)


if __name__ == '__main__':
    path_coupon = '../data/coupon(可以知道每个coupon包含的product，以及属于哪个campaign).csv'
    path_campaign_desc = '../data/campaign_desc(定义campaign属于何种type及其起止日期).csv'
    path_campaign_table = '../data/campaign_table(可以知道每个household收到的campaign).csv'
    couponUID_generate(path_coupon, path_campaign_desc, path_campaign_table)