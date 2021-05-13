import requests
from bs4 import BeautifulSoup
import io
from collections import Counter
import powerlaw
import matplotlib.pyplot as plt
import networkx as nx
from scipy.optimize import curve_fit


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

def ConstructGraph(ListOfPosts):
	G = nx.Graph()
	for i in ListOfPosts:
		G.add_node(i.username)
	for j in ListOfPosts:
		for k in j.responseto:
			G.add_edge(j.username, k)
	pos = nx.spring_layout(G, k=0.2)
	plt.figure(2, figsize=(30, 30))
	nx.draw(G, pos=pos)
	nx.draw_networkx_labels(G, pos=pos, font_color="red")
	plt.show()
	return(G)

def TableforGraph(G):
	ConnectedComponents = nx.connected_components(G)
	NumOfEdges = G.number_of_edges()
	NumOfNodes = G.number_of_nodes()
	##Diameter = nx.diameter(nx.connected_components(G))
	NumOfConnectedComponents = nx.number_connected_components(G)
	AverageClustering = nx.average_clustering(G)
	DegreeCentrality = nx.degree_centrality(G)
	AverageDegreeCentrality = sum(DegreeCentrality.values()) / len(DegreeCentrality)
	ClosenessCentrality = nx.closeness_centrality(G)
	AverageDegreeClosenessCentrality = sum(ClosenessCentrality.values()) / len(ClosenessCentrality)
	GraphTable = {
			"Number of edges": NumOfEdges,
			"Number of nodes": NumOfNodes,
			"Diameter": "To_Be_Added",
			"Number of connected components": NumOfConnectedComponents, 
			"Average clustering": AverageClustering,
			"Average degree centrality": AverageDegreeCentrality,
			"Average degree closeness centrality": AverageDegreeClosenessCentrality
	}

	return(GraphTable)

def CentralityHist(G):
	DegreeCentrality = nx.degree_centrality(G)
	plt.figure()
	plt.title("Degree centrality distribution")
	plt.hist(list(DegreeCentrality.values()))
	return plt.show()

def ClusteringHist(G):
	localClustering = nx.clustering(G)
	plt.figure()
	plt.title("Local clustering coefficient distribution")
	plt.hist(list(localClustering.values()))
	return plt.show()

def PowerLawCentrality(G):
	def func_powerlaw(x, m, c, c0):
		return c0 + x**m * c
	DegreeCentrality = nx.degree_centrality(G)
	DegreeCentrality_values = list(DegreeCentrality.values())
	DegreeCentrality_values = sorted(DegreeCentrality_values)
	centrality_count_dict = dict(Counter(DegreeCentrality_values))
	centrality_count = list(centrality_count_dict.values())
	rank = list(range(1,len(centrality_count)+1))
	popt, pcov = curve_fit(func_powerlaw, rank, centrality_count, maxfev=2000 )
	plt.plot(rank, func_powerlaw(rank, *popt), 'g-', label='power law')
	plt.plot(centrality_count,  rank, 'bo', label='data')
	plt.title("power law distribution of degree centrality")
	plt.legend()
	return plt.show()

def PowerLawClustering(G):
	def func_powerlaw(x, m, c, c0):
		return c0 + x**m * c
	localClustering = nx.clustering(G)
	localClustering_values = list(localClustering.values())
	localClustering_values = sorted(localClustering_values)
	clustering_count_dict = dict(Counter(localClustering_values))
	clustering_count = list(clustering_count_dict.values())
	rank = list(range(1,len(clustering_count)+1))
	popt, pcov = curve_fit(func_powerlaw, rank, clustering_count, maxfev=2000 )
	plt.plot(rank, func_powerlaw(rank, *popt), 'g-', label='power law')
	plt.plot(clustering_count,  rank, 'bo', label='data')
	plt.title("power law distribution of local clustering")
	plt.legend()
	return plt.show()

def main():
	with io.open("ForumContent.txt", "r", encoding="utf-8") as f:
		Text = f.read()
	soup = BeautifulSoup(Text, 'html.parser')
	posts = soup.find_all(id= lambda x: x and x.startswith("post60"))
	index = 1
	ListOfPosts = []
	ListOfLocations = []
	ListOfLengths = []
	for i in posts:
		responseto = []
		postnumber = index
		index += 1
		location = i.find(text= lambda x: x and x.startswith("Location: "))
		username = i.find(class_="bigusername").text
		comment = i.find(id= lambda x: x and x.startswith("post_message_")).text
		responses = i.find_all("strong")
		ListOfLocations.append(location)
		for j in responses:
			responseto.append(j.get_text())	
		postdate = i.find(class_="thead").text.strip()
		reputation = i.find(class_="smallfont").text.strip().replace("\n", " ").replace("\t", "")
		ListOfPosts.append(Post(postnumber, username, location, comment, postdate, reputation, responseto))
	for i in ListOfPosts:
		if i.username == "Supervision required":
			print("\n\n", i.postnumber, i.username, i.location, i.postdate, i.reputation, "Response to:", i.responseto, "\n")
	

	#count location occurrences
	def getList(dict):
		return list(dict.keys())

	location_count_dict = dict(Counter(ListOfLocations))
	count_values = list(location_count_dict.values()) #list of values of location occurrences
	count_values = sorted(i for i in count_values if i < 200)
	print(count_values)
	count_location = getList(location_count_dict) #list of locations, no dublicates and in same order as previous values
	location_counter = Counter(ListOfLocations)
	print(ListOfLengths)
	plt.bar(range(len(count_values)), count_values)#location occurrences
	plt.title("Location distribution")
	plt.show()

#	def func_powerlaw(x, m, c, c0):
#		return c0 + x**m * c
#	popt, pcov = curve_fit(func_powerlaw, count_values, centrality_values, maxfev=2000 )
#	plt.plot(centrality_count, func_powerlaw(centrality_count, *popt), 'g-', label='power law')
#	plt.plot(centrality_count,  centrality_values, 'bo', label='data')
#	plt.title("power law distribution of degree centrality")
#	plt.legend()
#	plt.show()

	

	#powerlaw distribution, can not be done with given values
	results = powerlaw.Fit(count_values)
	print(results.power_law.alpha)
	print(results.power_law.xmin)
	R, p = results.distribution_compare('power_law', 'lognormal')

	G = ConstructGraph(ListOfPosts)
	Table = TableforGraph(G)
	print(Table)

	CentralityHist(G)
	ClusteringHist(G)
	PowerLawCentrality(G)
	PowerLawClustering(G)


	

main()