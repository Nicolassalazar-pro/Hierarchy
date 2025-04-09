import requests
import json

data2 = None
comments = []

def print_info(answer):
    for i in range(len(answer)):
        print("Title: {}".format(answer[i]["title"]))
        print("URL: {}".format(answer[i]["url"]))
        if "body" in answer[i]:
            print("Body: {}".format(answer[i]["body"]))
        if "comments" in answer[i]:
            print("Comments:")
            for comment in answer[i]["comments"]:
                print(comment)

def dfs_reddit_comments(node):
    global comments
    if "data" in node:
        if "replies" in node["data"] and type(node["data"]["replies"]) == dict:
            temp = node["data"]["replies"]["data"]
            if "children" in temp:
                for child in temp["children"]:
                    if type(child) == dict:
                        dfs_reddit_comments(child)
        if "body" in node["data"] and node["data"]["body"] not in comments:
            body_comment = node["data"]["body"]
            comments.append(body_comment)

def reddit_scrapper():
    global data2, comments
    temp = open("links.txt", "r")
    urls_reddit = []

    for link in temp:
        urls_reddit.append(link.strip())

    temp.close()
    url = urls_reddit[0]
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    answer = []
    if response.status_code == 200:
        data = response.json()
        with open("reddit_data.json", "w") as f:
            json.dump(data, f, indent=4)
        
        print("Data saved to reddit_data.json")
        
        temp_url = "https://www.reddit.com"
        url_posts = []
        for child in data["data"]["children"]:
            if "permalink" in child["data"]:
                temp_url2 = child["data"]["permalink"][:-1]
                url_posts.append(temp_url + temp_url2 + ".json")
        
        url = ""
        for url in url_posts:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data2 = response.json()
                with open("post.json", "w") as f:
                    json.dump(data2, f, indent=4)
                
                print("Data saved in post.json from: {}".format(url))
                
                temp_dict = {}
                for child in data2[0]["data"]["children"]:
                    title_post = child["data"]["title"]
                    temp_dict["title"] = title_post
                    temp_dict["url"] = url
                    if child["data"]["selftext"] != "":
                        body_post = child["data"]["selftext"]
                        temp_dict["body"] = body_post
                
                comments = []
                for child in data2[1]["data"]["children"]:
                    if "replies" in child["data"]:
                        dfs_reddit_comments(child)
                    if "body" in child["data"] and child["data"]["body"] not in comments:
                        body_comment = child["data"]["body"]
                        comments.append(body_comment)
                
                temp_dict["comments"] = comments
                answer.append(temp_dict)
            else:
                print(f"Failed to retrieve data: {response.status_code}")
    else:
        print(f"Failed to retrieve data: {response.status_code}")
    
    print_info(answer)
    return answer

reddit_scrapper()