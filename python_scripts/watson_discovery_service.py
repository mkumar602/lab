"""test."""

import json
import random
from datetime import datetime

from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

DISCOVERY_APIKEY="O6ghm0MM2FryTK7S-sm3eEZ-RN-MM9ey5CI2-dKfhFmz"
#DISCOVERY_IAM_APIKEY="WKmkK8irdYUHmWVR2rP-g6JWAh9jdFIxRkIuJTo2fIkQ"
DISCOVERY_URL="https://api.eu-de.discovery.watson.cloud.ibm.com/instances/35911c5d-c1f9-4c01-9e69-d46e178213e5"
DISCOVERY_AUTH_TYPE="iam"
version="2020-08-30"


#project_id = "ab6c7e4e-c230-472f-958c-42dd43afa20f" #Apollo_PoCBox
#collection_ids = {
#    "Apollo_PoCBoX_Crawled_Collection": "ea31d67c-0c5e-25d0-0000-018ea43acb7d",
#}
project_id = "1f8f6333-0eee-483f-bf80-6b8a57308bf0" #Apollo LinkedIn Project
collection_ids = {
   "LinkedIn Collection": "784c9406-ff6f-de7f-0000-018e8b9b672b",
}

document_id = "6c7a438d882dc886fc6a89b1ec368458" #LinedIn Document

authenticator = IAMAuthenticator(DISCOVERY_APIKEY)
discovery = DiscoveryV2(
    version=version,
    authenticator=authenticator
)

discovery.set_service_url(DISCOVERY_URL)
response = discovery.get_project(project_id=project_id).get_result()
#print(json.dumps(response, indent=2))


response = discovery.list_collections(
  project_id=project_id
).get_result()

#print(json.dumps(response, indent=2))



response = discovery.list_documents(
    project_id=project_id, 
    collection_id="784c9406-ff6f-de7f-0000-018e8b9b672b", 
).get_result()
#print(json.dumps(response, indent=2))

response = discovery.get_document(
    project_id=project_id, 
    collection_id="784c9406-ff6f-de7f-0000-018e8b9b672b",
    document_id = "6c7a438d882dc886fc6a89b1ec368458", 
).get_result()
#print(json.dumps(response, indent=2))

response = discovery.query(
        project_id=project_id,
        collection_ids=["784c9406-ff6f-de7f-0000-018e8b9b672b"], 
        #query= "LinkedIn"
        query = "extracted_metadata.page_num=1"
).get_result()

with open("discovery_result.json", "w+") as file:
   file.write(json.dumps(response))
print(json.dumps(response, indent=2))


def get_html_df(data_df):
    """_summary_.

    Args:
        data_df (_type_): _description_

    Returns:
        _type_: _description_
    """
    return data_df.to_html(
        classes="mystyle", justify="center", index=False, col_space=30
    )


def get_wds_results_isda(query_value, collection_name, host=None):
    """_summary_.

    Args:
        query_value (_type_): _description_
        collection_name (_type_): _description_
        host (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    collection_id = collection_ids[collection_name]

    if query_value is not None:
        authenticator = IAMAuthenticator(DISCOVERY_APIKEY)
        discovery = DiscoveryV2(version="2020-08-30", authenticator=authenticator)

        discovery.set_service_url(DISCOVERY_URL)

        response = discovery.query(
            project_id=project_id, collection_ids=[collection_id], query=query_value
        ).get_result()

        with open("tmp/isda_discovery_result.json", "w+") as file:
            file.write(json.dumps(response))

    else:
        with open("tmp/isda_discovery_result.json") as file:
            response = json.loads(file.read())

    results_count = len(response["results"])
    result_df = pd.DataFrame(
        [
            response["results"][i]["document_passages"][0]["passage_text"]
            for i in range(results_count)
        ]
    )
    result_df["File Name"] = [
        response["results"][i]["extracted_metadata"]["filename"]
        for i in range(results_count)
    ]
    result_df.columns = ["Passage", "Document"]
    result_df["Party A"] = [
        "JPMORGAN CHASE BANK, NATIONAL ASSOCIATION"
    ] * result_df.shape[0]
    result_df[["Document", "Passage", "Party A"]]

    thresholds_list = []
    for j in range(results_count):
        text = response["results"][j]["text"][0]
        start = text.lower().find("threshold")
        start2 = text[:start].rfind(".")
        end2 = text[start:].find(".")
        thresholds_list.append(text[start2 : start + end2])

    result_df["Threshold"] = thresholds_list

    partys_list = []
    for j in range(results_count):
        temp = [
            i["text"]
            for i in response["results"][j]["enriched_text"][0]["entities"]
            if i["type"] == "Organization" and "bank" in i["text"].lower()
        ]
        if len(temp) != 0:
            partys_list.append(temp[random.randint(0, len(temp) - 1)])
        else:
            partys_list.append("JPMorgan Chase Bank")

    result_df["Party A"] = partys_list

    result_df_final = result_df[["Document", "Party A", "Passage", "Threshold"]]

    result_df_final = result_df_final.sort_values(by=["Document"])

    # result_df_final['Document']
    result_df_final["Document"] = result_df_final["Document"].apply(
        lambda x: update_as_link_isda(x, host)
    )

    result_df_html = result_df_final.to_html(
        classes="mystyle", justify="left", index=False, col_space=30, render_links=True
    )

    if "localhost" in str(host):
        result_df_html = result_df_html.replace(">http://localhost:8080/", ">")
    else:
        result_df_html = result_df_html.replace(">" + _DEMO_URL, ">")

    return result_df_html


def update_as_link_isda(x, host_name):
    """_summary_.

    Args:
        x (_type_): _description_
        host_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    if "localhost" in str(host_name):
        return "http://localhost:8080/" + str(x)
    else:
        return _DEMO_URL + str(x)


def get_wds_results(query_value, collection_name, host=None):
    """_summary_.

    Args:
        query_value (_type_): _description_
        collection_name (_type_): _description_
        host (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    collection_id = collection_ids[collection_name]

    if query_value is not None:
        authenticator = IAMAuthenticator(DISCOVERY_APIKEY)
        discovery = DiscoveryV2(version="2020-08-30", authenticator=authenticator)

        discovery.set_service_url(DISCOVERY_URL)

        response = discovery.query(
            project_id=project_id, collection_ids=[collection_id], query=query_value
        ).get_result()

        with open("tmp/discovery_result.json", "w+") as file:
            file.write(json.dumps(response))

    else:
        with open("tmp/discovery_result.json") as file:
            response = json.loads(file.read())

    filename_list = []
    policy_no_list = []
    date_of_loss_list = []

    for i in response["results"]:
        filename_list.append(i["extracted_metadata"]["filename"])
        if "policy_no" in i:
            policy_no_list.append(i["policy_no"])
        else:
            policy_no_list.append(None)

        if "date_of_loss" in i:
            date_of_loss_list.append(i["date_of_loss"])
        else:
            date_of_loss_list.append(None)

    results_from_discovery_df = pd.DataFrame(
        [filename_list, policy_no_list, date_of_loss_list]
    ).T
    results_from_discovery_df.columns = ["File Name", "Policy Number", "Date of Loss"]

    get_highlighting_text(response)
    more_attributes = []

    for i in range(results_from_discovery_df.shape[0]):
        if "localhost" in str(host):
            more_attributes.append(
                "http://localhost:8080/document_attributes" + str(i) + ".html"
            )
        else:
            more_attributes.append(_DEMO_URL + "document_attributes" + str(i) + ".html")

    results_from_discovery_df["More Attributes"] = more_attributes
    doc_numbers = []

    for i in range(1, 7):
        doc_numbers.append("Document " + str(i))

    results_from_discovery_df = results_from_discovery_df.head(6)
    results_from_discovery_df["No."] = doc_numbers
    results_from_discovery_df = results_from_discovery_df[
        ["No.", "File Name", "Policy Number", "Date of Loss", "More Attributes"]
    ]

    results_from_discovery_df2 = results_from_discovery_df.to_html(
        classes="mystyle",
        justify="center",
        index=False,
        col_space=30,
        render_links=True,
    )

    for i in more_attributes:
        results_from_discovery_df2 = results_from_discovery_df2.replace(
            ">" + i + "<", ">Attributes<"
        )

    results_from_discovery_df.to_csv(
        "tmp/results_from_wds" + str(datetime.now(tz=None))[:-7] + ".csv"
    )

    html_lines = get_more_info(response)

    return results_from_discovery_df2, html_lines


def get_highlighting_text(response):
    """_summary_.

    Args:
        response (_type_): _description_
    """
    attr_highlight_start = '<span style="background-color: #A5FF33">'
    attr_highlight_end = "</span>"

    document_attributes = []
    for each_result in response["results"]:
        html_text = each_result["html"]

        text_list = []
        for i in each_result["enriched_text"][0]["keywords"]:
            for j in i["mentions"]:
                text_list.append(j["text"])
        text_list2 = set(text_list)

        for i in text_list2:
            begin = html_text.find(i)
            if html_text[begin - 1] != "<" and html_text[begin + len(i)] != "/":
                html_text = html_text.replace(
                    i, attr_highlight_start + i + attr_highlight_end
                )

        res = {}
        for k in each_result["enriched_text"][0]["entities"]:
            res[k["text"]] = k["type"]

        res2 = {}
        for each_z in res:
            if res[each_z] != "Number":
                res2[each_z] = res[each_z]

        for i in res2:
            html_text = html_text.replace(
                i,
                i
                + attr_highlight_start
                + " ["
                + str(res[i]).upper()
                + "]"
                + attr_highlight_end,
            )

        document_attributes.append(html_text)

    k = 0

    for i in document_attributes:
        with open("./static/document_attributes" + str(k) + ".html", "w+") as file:
            file.write(i)
        k += 1


def get_more_info(data, doc_number=None):
    """_summary_.

    Args:
        data (_type_): _description_
        doc_number (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    html_lines = []

    if doc_number is None:
        docs_list = [1]
    else:
        docs_list = []
        docs_list.append(doc_number)

    for number in docs_list:
        html_lines.append("------------------------------------------------")

        if "enriched_policy_no" in data["results"][number].keys():
            html_lines.append(
                "Policy Number "
                + data["results"][number]["enriched_policy_no"][0]["entities"][0][
                    "text"
                ]
            )

        if "enriched_date_of_loss" in data["results"][number].keys():
            html_lines.append(
                "Date of Loss "
                + data["results"][number]["enriched_date_of_loss"][0]["entities"][0][
                    "text"
                ]
            )

        text = data["results"][number]["text"][0]
        text_list = text.split()

        html_lines.append("STUDENT PROPERTY LOSS NOTICE")

        skip = 0
        for i in data["results"][number]["enriched_text"][0]["entities"]:
            pre_text = ""

            if skip != 1:
                if "Page 2 of 2" in i["text"]:
                    skip = 1

                if (
                    i["type"] != "Number"
                    and "Page 2 of 2" not in i["text"]
                    and "police" not in i["text"].lower()
                    and "report" not in i["text"].lower()
                ):
                    if i["type"] == "Organization":
                        html_lines.append("-------------")
                    if i["type"] == "Money" and i["text"] in text_list:
                        if text_list[text_list.index(i["text"]) - 1] == "charge":
                            pre_text = (
                                text_list[text_list.index(i["text"]) - 2]
                                + " "
                                + text_list[text_list.index(i["text"]) - 1]
                            )
                        else:
                            pre_text = text_list[text_list.index(i["text"]) - 1]

                    if i["type"] == "EmailAddress" and i["text"] in text_list:
                        pre_text = text_list[text_list.index(i["text"]) - 1]

                    if i["type"] == "Date" and i["text"] in text_list:
                        if text_list[text_list.index(i["text"]) - 1] == "loss:":
                            pre_text = (
                                text_list[text_list.index(i["text"]) - 3]
                                + " "
                                + text_list[text_list.index(i["text"]) - 2]
                                + " "
                                + text_list[text_list.index(i["text"]) - 1]
                            )
                        else:
                            pre_text = text_list[text_list.index(i["text"]) - 1]

                    elif i["type"] == "Date":
                        text.find(i["text"])
                        start = text[: text.find(i["text"]) - 1].rfind(" ")
                        end = text.find(i["text"])
                        pre_text = text[start + 1 : end]

                    html_lines.append(pre_text + " " + i["text"])

    extra_info_df = pd.DataFrame()
    extra_info_df["Property Value"] = [i for i in html_lines if i != "\n"]

    # extra_info_df.to_csv('tmp/extra_info_df.csv')

    extra_info_df = pd.read_csv("tmp/extra_info_df.csv")
    extra_info_df["Attribute"] = [
        "-------------",
        "Policy Number",
        "Date of Loss",
        "Document Type",
        "-------------",
        "Name",
        "City",
        "State",
        "Zip Code",
        "Contact",
        "Mobile",
        "Mobile",
        "-------------",
        "13",
        "-------------",
        "School",
        "State",
        "Zip Code",
        "Mobile",
        "E-Mail",
        "City",
        "State",
        "22",
        "-------------",
        "24",
        "Term",
        "Limit",
        "Deductible",
        "E-Mail",
    ]
    extra_info_df["Value"] = extra_info_df.apply(
        lambda row: row["Property Value"]
        .replace(row["Attribute"], "")
        .replace(":", "")
        .strip(),
        axis=1,
    )
    extra_info_df2 = extra_info_df[["Attribute", "Value"]].copy()
    extra_info_df_html = extra_info_df2.to_html(
        classes="mystyle2", justify="center", index=False, col_space=30
    )

    return html_lines, extra_info_df_html
