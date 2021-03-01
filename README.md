# gym-auto-registration

A small module for automating interaction with the MotionVibe member portal. The module above features 3 truly useful functions:
1. quick_reg(cookies) -> Automated registration for nearest appt in favorites
2. unreg_nearest(cookies) -> Manually triggered, automated unregistration from nearest appt in favorites
3. reg_all(cookies) -> Manually triggered, automated registration for all available appts in favorites

The cookies parameter in each case refers to an object containing the cookies from a previous log in session, which can be obtained by configuring and running the get_cookie_profile(user_id, u_name, p_word) method.

Happy Automating!

Built with python 3.8
