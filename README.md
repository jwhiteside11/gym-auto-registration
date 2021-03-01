# gym-auto-registration

A small module for automating interaction with the MotionVibe member portal. The module above features 3 truly useful functions:
1. quick_reg(c) -> Automated registration for nearest appt in favorites
2. unreg_nearest(c) -> Manually triggered, automated unregistration from nearest appt in favorites
3. reg_all(c) -> Manually triggered, automated registration for all available appts in favorites

The c parameter in each case refers to an object containing the cookies from a previous log in session, which can be obtained by configuring and running the get_cookie_profile(user_id, u_name, p_word) method.

The user will need to insert their gym's MotionVibe Login Portal URL and appropriate file paths by replacing <UPPER> throughout the file.

Happy Automating!

Built with python 3.8
