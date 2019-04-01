from pprint import PrettyPrinter
import itertools

pp = PrettyPrinter(indent = 4)

TEAM_A = 'SRH'
TEAM_B = 'RR'
MAX_CREDITS = 100.0
ROLES = ["WK", "BAT", "AR", "BOWL"]


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


	def is_role_full(self, role):
		return len(self.roles[role]) >= self.combination[role]


	def is_team_complete(self):
		return self.players_count == 11 

	def show(self):
		for role in self.roles.keys():
			print (role)
			for player in self.roles[role]:
				print (player)


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


	def add_players_for_role(self, role, players, min_credits_required_after_filling_a_role):
		self.remove_players_with_role(role)
		meets_constrainsts = True
		for player in players:
			added, reason = self.add_player(player)
			if not added:
				meets_constrainsts = False
				break
		if not meets_constrainsts:
			self.remove_players_with_role(role)
			return False	
		return True


def add_players_to_team(player_pool, combination, min_credits_required_after_filling_a_role):
	player_combinations = dict() 
	for key in combination.keys():
		player_combinations[key] = list(set(itertools.combinations(player_pool.roles[key], combination[key])))
	teams_for_this_combination = list()
	team = Team(combination)
	for i in player_combinations[ROLES[0]]:
		team.add_players_for_role(ROLES[0], i, min_credits_required_after_filling_a_role)
		for j in player_combinations[ROLES[1]]:
			team.add_players_for_role(ROLES[1], j, min_credits_required_after_filling_a_role)
			for k in player_combinations[ROLES[2]]:
				team.add_players_for_role(ROLES[2], k, min_credits_required_after_filling_a_role)
				for l in player_combinations[ROLES[3]]:
					if team.add_players_for_role(ROLES[3], l, min_credits_required_after_filling_a_role):
						teams_for_this_combination.append(team)
	return teams_for_this_combination
	

def build_teams(player_pool, combination):
	lowest_credits_per_role_for_this_combination = dict()
	for role in ROLES:
		lowest_credits_per_role_for_this_combination[role] = sum([player.credits for player in player_pool.roles[role][-1 * combination[role]: ]])
	min_credits_required_after_filling_a_role = dict()
	for i in range(len(ROLES) - 1):
		cur_role = ROLES[i]
		min_credits_required_after_filling_a_role[cur_role] = sum([lowest_credits_per_role_for_this_combination[role] for role in ROLES[i + 1: ]])
	return add_players_to_team(player_pool, combination, min_credits_required_after_filling_a_role)


if __name__=='__main__':
	import sys

	player_pool = Pool()
	with open(sys.argv[1], 'r') as players_stats:
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

	all_teams.sort(key = lambda x: x.points, reverse = True)

	for team in all_teams:
		print("\n\n")
		print ("Team points: {}".format(team.points))
		team.show()




