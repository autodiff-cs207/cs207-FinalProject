import api
from threading import Thread
import random
import numpy as np
import math


# create a thread object that returns the thread results
# adapted from kindall on stackoverflow
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=()):
        Thread.__init__(self, group, target, name, args)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

# multi-dimensional Newton's method
def vectorNewton(input_function,tolerance=1e-5, num_starting_vals = 20, 
	starting_val_range = (-1000,1000), starting_val_dict_list=None, verbose=True):

	# initialize our list
	if not starting_val_dict_list:
		starting_val_dict_list = []

	# find one root 
	def find_root(vf,starting_val_dict, max_iter,tol):
		
		val_dict = starting_val_dict

		error_list = []
		fx = f.get_val(val_dict)
		i = 0
		all_dim_dist = math.inf

		# if we haven't done too many iterations and we're still greater than our tolerance 
		while i < max_iter and  all_dim_dist > tol:
			i+=1

			abs_fx = [abs(val) for val in fx]
			all_dim_dist = np.sum(abs_fx)
			all_dim_dist = np.linalg.norm(fx,ord=2)

			# make a list of errors so we can check Newton's method is working
			error_list += [np.sum(abs_fx)]

			# get jacobian, move to new point
			try:
				dx = vf.dict_list_to_array(vf.get_der(val_dict))

				# need to update all new values of value dictionary
				delta = np.linalg.solve(np.array(dx),-1*np.array(fx))

				# update dictionary
				for i,val in enumerate(vf.name_list):
					val_dict[val] = val_dict[val] + delta[i]
				new_fx = vf.get_val(val_dict)
				fx = new_fx

			# avoid dividing by zero 
			except:
				print("Tried to divide by zero!")
				return
		return ([val_dict[var] for var in vf.name_list] , vf.get_val(val_dict), i,error_list)

	# function takes value and list, returns true if value is within diff_tol of any value
	# in the list, false otherwise.
	def is_close_vector_lists(v,lst,diff_tol=1e-6):
		for ele in lst:
			l = [abs(v[i]-ele[i]) for i in range(len(v))]
			if np.sum(l)<diff_tol:
				return False
		return True 


	f = input_function

	# adjust starting value list to agree with number of requested starting values 
	while len(starting_val_dict_list)<num_starting_vals:
		starting_val_dict_to_add = {}
		for var in f.name_list:
			starting_val_dict_to_add[var] = random.randint(starting_val_range[0],starting_val_range[1])
		starting_val_dict_list.append(starting_val_dict_to_add)

	max_iter = 100 # maybe user should be able to choose this? 
	results = []
	roots = []

	# start threads 
	for i in range(len(starting_val_dict_list)):
		thread = ThreadWithReturnValue(target=find_root, 
			args=(f,starting_val_dict_list[i],max_iter,tolerance))
		thread.start()
		full_result = thread.join()

		# if didn't catch exception in find_root 
		if full_result:
			root_result = full_result[0]

			# check if root already in list 
			if (is_close_vector_lists(root_result, roots)):
				roots.append(root_result)
				results.append(full_result)

	# for testing, choose verbose 
	if verbose:
		return results
	else:
		return roots


def quasi_newton(input_function,tolerance):
	pass


def multiple_function_root_finder(input_function, lr=0.01, adadelta=False):
	pass


if __name__ == "__main__":
	x=api.Variable('x')
	y=api.Variable('y')

	# answer is [0,2,-3]
	single_function_to_solve=x**api.Constant('a_1', 3)+x**api.Constant('a_2', 2)-api.Constant('a_3', 6)*x
	answer_for_single=single_function_root_finder(single_function_to_solve)
	answer_for_single=single_function_root_finder(single_function_to_solve,adadelta=True)


	# answer is [(x=1,y=4),(x=2,y=3)]
	function_1=x*y-api.Constant('b_1', 4)*x-api.Constant('b_2', 2)*y+api.Constant('b_3', 8)
	function_2=x*y-api.Constant('c_1', 3)*x-api.Constant('c_2', 1)*y+api.Constant('c_3', 3)
	multiple_function_to_solve=[function_1,function_2]
	answer_for_multiple=multiple_function_root_finder(multiple_function_to_solve)
	answer_for_multiple=multiple_function_root_finder(multiple_function_to_solve,adadelta=True)