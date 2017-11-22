import os
import sys
import vk_api

ACCOUNT_FILE = 'account.txt'
GROUP_ID = sys.argv[1]

def main():
    needs_restart = False
    if not os.path.exists(ACCOUNT_FILE):
        open(ACCOUNT_FILE, 'a').close()
        print '{} created!'.format(ACCOUNT_FILE)
        needs_restart = True
    else:
        with open(ACCOUNT_FILE, 'r') as file:
            login, password = file.read().strip().split(':')
    
    if needs_restart:
        print 'Fill necessary files in and restart the script.'
        return
    
    api = auth(login, password)
    if api['success']:
        admins_find(api['api'], api['vk_session'], GROUP_ID)

def admins_find(api, vk_session, group_id):
    tools = vk_api.VkTools(vk_session)
    group_members = get_group_members(tools, group_id)
    avatars = get_all_photos(api, group_id)
    if not avatars:
        print 'group has no avatars.'
        return
    digits = get_digits(avatars)
    matching = find_matching(group_members, digits)
    if len(digits) == 1:
        print 'only 1 avatar loader found. printing all possible candidates: \n{}'.format(matching)
        return
    matching_with_friends = get_friends(matching)
    matching_pairs = []
    for user in matching:
        for user2 in matching_with_friends:
            if user in matching_with_friends[user2]['items'] and str(user)[-3:] != str(user2)[-3:] and {user, user2} not in matching_pairs:
                matching_pairs.append({user, user2})
    matching_pairs = [list(item) for item in matching_pairs]
    if matching_pairs:
        for item in matching_pairs:
            print item
    else:
        print 'several unconnected avatar uploaders found: \n{}'.format(matching)
    
    
def auth(login, password):
    api = {}
    vk_session = vk_api.VkApi(login, password)
    try:
        vk_session.auth()
        api['api'] = vk_session.get_api()
        api['vk_session'] = vk_session
        api['success'] = 1
        print '### auth {0} success! ###'.format(login)
    except vk_api.AuthError as error_message:
        print '{0}: {1}'.format(self.login, str(error_message))
        api['success'] = 0
    return api

def get_group_members(tools, group_id):
    group_members = tools.get_all('groups.getMembers', 1000, {'group_id': group_id})
    return group_members['items']

def get_all_photos(api, group_id):
    all_photos = api.photos.get(owner_id = '-{}'.format(group_id), album_id = 'profile')
    if all_photos['count']:
        return all_photos['items']

def get_digits(photos):
    digits = set([item['photo_75'].split('/')[-3][-3:] for item in photos])
    return digits

def find_matching(members, digits):
    matching = [member for member in members if str(member)[-3:] in digits]
    return matching

def get_friends(users):
    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method_one_param('friends.get', key='user_id', values=users)
    return friends.result

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Shutting down...'
        sys.exit(0)
