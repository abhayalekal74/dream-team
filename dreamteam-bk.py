from pprint import PrettyPrinter
from itertools import combinations

pp = PrettyPrinter(indent = 4)

TEAM_A = 'SRH'
TEAM_B = 'RR'
MAX_CREDITS = 100.0
CATEGORIES = ["WK", "BAT", "AR", "BOWL"]


class Pool:
	def __init__(self):
		self.roles = dict(zip(CATEGORIES, [[], [], [], []]))
		self.teams = {TEAM_A: list(), TEAM_B: list()}

	
	def add_player(self, player):
		self.roles[player.role].append(player)
		self.teams[player.team].append(player)


	def organize(self):
		for key in self.roles.keys():
			self.roles[key].sort(key = lambda x: x.credits, reverse = True)


	def show(self):
		print ("Players pool")
		for role, players in self.roles.items():
			print ("\n", role, "\n")
			for player in players:
				print (player)
			print ("\n")
			
		
class Player:
	def __init__(self, role, team, name, credits, points):
		self.role = role
		self.team = team
		self.name = name
		self.credits = float(credits)
		self.points = float(points)


	def __str__(self):
		return "{}, {}, {}, {}, {}".format(self.name, self.role, self.team, self.credits, self.points)


class Team:

	PLAYER_ADDED = -1
	TEAM_COMPLETE = 0
	ROLE_FULL = 1
	MAX_PLAYERS_FROM_TEAM = 2
	NOT_ENOUGH_CREDITS = 3


	def __init__(self, combination):
		self.players = list()
		self.combination = combination
		self.points = 0.0
		self.players_count = 0
		self.counts = {TEAM_A: 0, TEAM_B: 0}
		self.credits_remaining = MAX_CREDITS 
		self.roles = dict(zip(CATEGORIES, [[], [], [], []])) 


	def add_player(self, player):
		if len(self.players) >= 11:
			return False, TEAM_COMPLETE
		elif len(self.roles[player.role]) >= self.combination[player.role]:
			return False, ROLE_FULL
		elif self.counts[player.team] >= 7:
			return False, MAX_PLAYERS_FROM_TEAM
		elif player.credits > self.credits_remaining:
			return False, NOT_ENOUGH_CREDITS
		else:
			self.players.append(player)
			self.roles[player.role].append(player)
			self.players_count += 1
			self.counts[player.team] += 1
			self.credits_remaining -= player.credits
			self.points += player.points
			if len(self.players) == 11:
				return True, TEAM_COMPLETE
			else:
				return True, PLAYER_ADDED


	def is_category_full(self, category):
		return len(self.roles[category]) >= self.combination[category]


	def is_team_complete(self):
		return len(self.players) == 11 


	def get_team(self):
		return self.players

	def remove_players(self, n = 1, category = None):
		if category:
			for i in range(len(self.players) - 1, -1, -1):
				player = self.players[i]
				if player.role == category:
					del self.players[i]
		else:
			for i in range(len(self.players) - 1, max(len(self.players) - n - 2, 0), -1):
				del self.players[i]
			

def add_players_to_team(player_pool, team, min_credits_required_after_filling_a_category):
	do_not_add_players_from = None # If set to a team, players from that team won't be added
	c = 0
	while c < len(CATEGORIES):
		category = CATEGORIES[c]
		category_full = False
		i = 0
		added_player_indices_teamwise = {team_A: list(), team_B: list()}
		added_player_indices = list()
		while i < len(player_pool.role[category]):
			player = player_pool.role[category][i]
			i += 1			
			if player.team == do_not_add_players_from:
				continue
			player_added, reason = team.add_player(player)
			if player_added:
				added_player_indices_teamwise[player.team].append(i)
				added_player_indices.append(i)
				if reason == Team.TEAM_COMPLETE:
					yield team.get_team()
			else:
				if reason == Team.TEAM_COMPLETE:
					yield team.get_team()
				elif reason == Team.ROLE_FULL:
					if team.credits_remaining < min_credits_required_after_filling_a_category[category]:
						team.remove_players(n = 1)
						last_added_player = added_player_indices[-1]
						del added_player_indices[-1]
						del added_player_indices_teamwise[player.team][-1]
						i = last_added_player + 1
					break
				elif reason == Team.MAX_PLAYERS_FROM_TEAM:
					do_not_add_players_from = player.team
				elif reason == Team.NOT_ENOUGH_CREDITS:
					if i == len(player_pool.role[category]): # No player can be fit into the team with the credits remaining, start removing players


def build_teams(player_pool, combination):
	lowest_credits_per_category_for_this_combination = dict()
	for category in CATEGORIES:
		lowest_credits_per_category_for_this_combination[category] = sum([player.credits for player in player_pool.roles[category][-1 * combination[category]: ]])
	min_credits_required_after_filling_a_category = dict()
	for i in range(len(CATEGORIES) - 1):
		cur_category = CATEGORIES[i]
		min_credits_required_after_filling_a_category[cur_category] = sum([lowest_credits_per_category_for_this_combination[category] for category in CATEGORIES[i + 1: ]])
	
	team = Team(combination)
	return add_players_to_team(player_pool, team, min_credits_required_after_filling_a_category)


if __name__=='__main__':
	import sys

	player_pool = Pool()
	with open(sys.argv[1], 'r') as players_stats:
		for player_stats in players_stats.readlines():
			player_pool.add_player(Player(*player_stats.split(',')))

	player_pool.organize()
	player_pool.show()
				
	all_combinations = 	[
							[1, 3, 2, 5],
							[1, 3, 3, 4],
							[1, 4, 1, 5],
							[1, 4, 2, 4],
							[1, 4, 3, 3],
							[1, 5, 1, 4],
							[1, 5, 2, 3]
						]

	all_teams = list()	
	for combination in all_combinations:
		mapped_combination = dict(zip(CATEGORIES, combination))
		all_teams.append(build_teams(player_pool, mapped_combination))

	




