"""test."""

import yaml
import pandas as pd

with open("config.yaml", "r") as yamlfile:
    config_values = yaml.load(yamlfile, Loader=yaml.FullLoader)


def get_view_table():
    """_summary_.

    Returns:
        _type_: _description_
    """
    temp = pd.DataFrame.from_dict(config_values["view"]).T
    temp

    doc = []
    layout_name = []
    uuid = []

    for each_col in temp.columns:
        for each_row in temp.index:
            if "nan" not in str(temp.loc[each_row, each_col]):
                doc.append(each_row.replace("_", " ").title())
                layout_name.append(
                    each_col.replace("_", " ").replace("uuid", " ").title()
                )
                uuid.append(str(temp.loc[each_row, each_col]))

    view_df = pd.DataFrame([doc, layout_name, uuid]).T
    view_df.columns = ["Document", "Layout Name", "Layout UUID"]
    view_df_html = view_df.to_html(
        index=False,
        index_names=False,
        table_id="data",
        classes="mystyle",
        justify="center",
        col_space=30,
        render_links=True,
    )

    return view_df_html


def get_create_table():
    """_summary_.

    Returns:
        _type_: _description_
    """
    create_df = pd.DataFrame(config_values["create"]).T.reset_index()
    create_df.columns = ["Document", "Flow UUID", "Layout UUID"]
    create_df["Document"] = create_df["Document"].apply(
        lambda x: x.replace("_", " ").title()
    )
    create_df_html = create_df.to_html(
        index=False,
        index_names=False,
        table_id="data",
        classes="mystyle",
        justify="center",
        col_space=30,
        render_links=True,
    )

    return create_df_html
