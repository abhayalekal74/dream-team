from pprint import PrettyPrinter
import sys
from operator import itemgetter 
import itertools

pp = PrettyPrinter(indent = 4)

TEAM_A = ''
TEAM_B = ''
MAX_CREDITS = 100.0
N_TOP_TEAMS = 5
ROLES = ["WK", "BAT", "AR", "BOWL"]

team_id = 0
teams_map = dict()
player_teams_map = dict()


class Pool:
	def __init__(self):
		self.roles = dict(zip(ROLES, [[], [], [], []]))
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
		self.combination = combination
		self.points = 0.0
		self.players_count = 0
		self.counts = {TEAM_A: 0, TEAM_B: 0}
		self.credits_remaining = MAX_CREDITS 
		self.roles = dict(zip(ROLES, [[], [], [], []])) 


	def are_roles_full(self):
		for role in ROLES:
			if len(self.roles[role]) < self.combination[role]:
				return False
		return True


	def is_team_complete(self):
		return self.players_count == 11 


	def get_team(self):
		team_repr = list()
		team_repr.append(self.points)
		team_repr.append(self.credits_remaining)
		data = ""
		for role in self.roles.keys():
			data += role + ": "
			player_names = list()
			for player in self.roles[role]:
				player_names.append(player.name)
			data += ", ".join(player_names)
			data += "\n"
		team_repr.append(data)
		return team_repr


	def add_player(self, player):
		if self.players_count >= 11:
			return False, self.TEAM_COMPLETE
		elif len(self.roles[player.role]) >= self.combination[player.role]:
			return False, self.ROLE_FULL
		elif self.counts[player.team] >= 7:
			return False, self.MAX_PLAYERS_FROM_TEAM
		elif player.credits > self.credits_remaining:
			return False, self.NOT_ENOUGH_CREDITS
		else:
			self.roles[player.role].append(player)
			self.players_count += 1
			self.counts[player.team] += 1
			self.credits_remaining -= player.credits
			self.points += player.points
			return True, self.PLAYER_ADDED


	def remove_players_with_role(self, role):
		players_with_this_role = self.roles[role]
		if players_with_this_role:
			for player in players_with_this_role:
				self.counts[player.team] -= 1
				self.players_count -= 1
				self.credits_remaining += player.credits
				self.points -= player.points
			self.roles[role].clear()


	def add_players_for_role(self, role_players_map, min_credits_required_after_filling_a_role):
		for role in ROLES:
			for player in role_players_map[role]: 
				added, reason = self.add_player(player)
				if not added:
					return False
			if self.credits_remaining < min_credits_required_after_filling_a_role[role]:
				return False	
		return True
	
	
	def get_players(self):
		players = list()
		for key, val in self.roles.items():
			players += val
		return players


def save_team(team_repr, players):
	global teams_map, team_id, player_teams_map
	team_id += 1
	teams_map[team_id] = team_repr
	for player in players:
		try:
			teams_with_this_player = player_teams_map[player.name]
		except KeyError:
			teams_with_this_player = list()
			player_teams_map[player.name] = teams_with_this_player
		teams_with_this_player.append(team_id)
	return team_id


def add_players_to_team(player_pool, combination, min_credits_required_after_filling_a_role):
	player_combinations = dict() 
	for key in combination.keys():
		player_combinations[key] = list(set(itertools.combinations(player_pool.roles[key], combination[key])))
	teams_for_this_combination = list()
	for i in player_combinations[ROLES[0]]:
		for j in player_combinations[ROLES[1]]:
			for k in player_combinations[ROLES[2]]:
				for l in player_combinations[ROLES[3]]:
					team = Team(combination)
					added = team.add_players_for_role(dict(zip(ROLES, [i, j, k, l])), min_credits_required_after_filling_a_role)
					if added and team.is_team_complete() and team.are_roles_full():
						teams_for_this_combination.append(save_team(team.get_team(), team.get_players()))
	return teams_for_this_combination
	

def build_teams(player_pool, combination):
	print ("Building teams for combination", combination)
	lowest_credits_per_role_for_this_combination = dict()
	for role in ROLES:
		lowest_credits_per_role_for_this_combination[role] = sum([player.credits for player in player_pool.roles[role][-1 * combination[role]: ]])
	min_credits_required_after_filling_a_role = dict()
	for i in range(len(ROLES) - 1):
		cur_role = ROLES[i]
		min_credits_required_after_filling_a_role[cur_role] = sum([lowest_credits_per_role_for_this_combination[role] for role in ROLES[i + 1: ]])
	min_credits_required_after_filling_a_role[ROLES[3]] = 0
	return add_players_to_team(player_pool, combination, min_credits_required_after_filling_a_role)


def print_top_teams(criterion, top_teams):
	print ("\n", criterion)
	for team in top_teams: 
		print ("Team points: {}, Credits remaining: {}".format(team[0], team[1]))
		print (team[2])


def print_top_teams_from_map(criterion, sort_key, reverse = False, secondary_index = -1, reverse_secondary_index = False):
	if secondary_index == -1:
		top_teams = [i[1] for i in sorted(teams_map.items(), key = lambda x: x[1][sort_key], reverse = reverse)[:N_TOP_TEAMS]]
	else:
		top_teams = [i[1] for i in sorted(teams_map.items(), key = lambda x: x[1][sort_key], reverse = reverse)]
		top_teams.sort(key = lambda x: x[secondary_index], reverse = reverse_secondary_index)
		top_teams = top_teams[:N_TOP_TEAMS]
	print_top_teams(criterion, top_teams)


if __name__=='__main__':
	fixture = sys.argv[1]
	mandatory_players = [player.strip() for player in sys.argv[2].split(',')] if len(sys.argv) > 2 else None
	TEAM_A, TEAM_B = fixture.split('v')

	player_pool = Pool()
	with open(fixture, 'r') as players_stats:
		for player_stats in players_stats.readlines():
			player_pool.add_player(Player(*player_stats.split(',')))

	player_pool.organize()
	#player_pool.show()
				
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
		mapped_combination = dict(zip(ROLES, combination))
		all_teams += build_teams(player_pool, mapped_combination)

	print ("\nTotal teams", len(teams_map))

	print_top_teams_from_map("Most points", 0, reverse = True)
	print_top_teams_from_map("Credits maximized", 1, secondary_index = 0, reverse_secondary_index = True)

	if mandatory_players:
		teams_with_mandatory_players = list()
		for player in mandatory_players:
			try:
				teams_with_mandatory_players.append(player_teams_map[player])
			except KeyError:
				pass
		common_teams = [teams_map[id] for id in set(teams_with_mandatory_players[0]).intersection(*teams_with_mandatory_players)]
		if common_teams:
			common_teams.sort(key = lambda x: x[0], reverse = True)
			print_top_teams("Most points including {}".format(", ".join(mandatory_players)), common_teams[:N_TOP_TEAMS])	
			common_teams.sort(key = lambda x: x[1], reverse = False)
			print_top_teams("Credits maximized including {}".format(", ".join(mandatory_players)), common_teams[:N_TOP_TEAMS])	
