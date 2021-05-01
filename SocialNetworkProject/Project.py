import requests
from bs4 import BeautifulSoup
import io

class Post:
	def __init__(self, postnumber, username, location, comment, postdate, reputation, responseto):
		self.postnumber = postnumber
		self.username = username
		self.location = location
		self.comment = comment
		self.postdate = postdate
		self.reputation = reputation
		self.responseto = responseto

def DownloadAllForumMessages(): ## Downloads all the pages on the forum that are related to this thread, takes like a minute to run so only use if you want to update the stored file 
	url = "https://www.city-data.com/forum/health-wellness/3245374-have-you-had-covid-vaccine-side.html"

	RequestedPage = requests.get(url)
	RequestedPageAsText = RequestedPage.text

	soup = BeautifulSoup(RequestedPageAsText, 'html.parser')

	numofpages = int(soup.find(class_="vbmenu_control").text.split()[-1])

	AllPagesText = ""

	for i in range(1, numofpages + 1):
		if i == 1:
			url = "https://www.city-data.com/forum/health-wellness/3245374-have-you-had-covid-vaccine-side.html"
		else:
			url = "https://www.city-data.com/forum/health-wellness/3245374-have-you-had-covid-vaccine-side-".strip() + str(i).strip() + ".html".strip()
		RequestedPage = requests.get(url)
		RequestedPageAsText = RequestedPage.text
		AllPagesText += RequestedPageAsText
	with io.open("ForumContent.txt", "w", encoding="utf-8") as f:
		f.write(AllPagesText)

def main():
	with io.open("ForumContent.txt", "r", encoding="utf-8") as f:
		Text = f.read()
	soup = BeautifulSoup(Text, 'html.parser')
	posts = soup.find_all(id= lambda x: x and x.startswith("post60"))
	index = 1
	ListOfPosts = []
	for i in posts:
		responseto = []
		postnumber = index
		index += 1
		location = i.find(text= lambda x: x and x.startswith("Location: "))
		username = i.find(class_="bigusername").text
		comment = i.find(id= lambda x: x and x.startswith("post_message_")).text
		responses = i.find_all("strong")
		for j in responses:
			responseto.append(j.get_text())
		postdate = i.find(class_="thead").text.strip()
		reputation = i.find(class_="smallfont").text.strip().replace("\n", " ").replace("\t", "")
		ListOfPosts.append(Post(postnumber, username, location, comment, postdate, reputation, responseto))
	for i in ListOfPosts:
		print("\n\n", i.postnumber, i.username, i.location, i.postdate, i.reputation, "Response to:", i.responseto, "\n")

main()