from InstagramAPI import InstagramAPI
import json
from typing import List, Any

# Credentials is just a python file with username, password, and whitelist as variables.
import credentials

whitelist = credentials.whitelist


class InstagramAccount(object):
    def __init__(self, login_name: str, password: str):
        self.login_name = login_name
        self.__account = InstagramAPI(username=self.login_name, password=password)
        self.login()
        self.user_id = self.__account.username_id
        self.whitelist = list()

        self.add_users_to_whitelist(whitelist)

    @property
    def unloyal_hoes(self):
        return self.get_unloyal_hoes()

    @property
    def num_unloyal_hoes(self):
        return len(self.unloyal_hoes)

    @property
    def following(self):
        return self.get_following()

    @property
    def num_following(self):
        return len(self.following)

    @property
    def followers(self):
        return self.get_followers()

    @property
    def num_followers(self):
        return len(self.followers)

    def add_users_to_whitelist(self, users: List[Any], debug: bool = False, using_ids=True):
        for user in users:
            if using_ids:
                self.add_user_to_whitelist(username=user, debug=debug)
            else:
                self.add_user_to_whitelist(username=self.get_id_by_username(user), debug=debug)

    def add_user_to_whitelist(self, username: str, debug: bool = False):
        found = self.__account.searchUsername(username)
        if found:
            self.add_id_to_whitelist(self.__account.LastJson['user']['pk'])
            if debug:
                print(f"Added user: {self.__account.LastJson['user']['pk']} to whitelist.")
        elif debug:
            print(f"Could not find ID for user: {username}.")

    def add_id_to_whitelist(self, userID):
        if userID not in self.whitelist:
            self.whitelist.append(userID)

    def get_followers(self):
        followers = list()
        next_max_id = True
        while next_max_id:
            if next_max_id is True:
                next_max_id = ''
            self.__account.getUserFollowers(self.user_id, maxid=next_max_id)
            followers.extend(self.__account.LastJson.get('users', []))
            next_max_id = self.__account.LastJson.get('next_max_id', '')

        return {
            f['pk']: f
            for f in followers
        }

    def get_following(self):
        following = list()
        next_max_id = True
        while next_max_id:
            if next_max_id is True:
                next_max_id = ''
            self.__account.getUserFollowings(self.user_id, maxid=next_max_id)
            following.extend(self.__account.LastJson.get('users', []))
            next_max_id = self.__account.LastJson.get('next_max_id', '')

        return {
            f['pk']: f
            for f in following
        }

    def get_timeline_feed(self):
        return self.__account.getTimeline()

    def unfollow_user_id(self, userid):
        self.__account.unfollow(userId=userid)

    def follow_user_id(self, userid):
        self.__account.follow(userId=userid)

    def get_unloyal_hoes(self):
        following_ids = set(self.following.keys())
        follower_ids = set(self.followers.keys())

        if len(following_ids) > len(follower_ids):
            return list(following_ids - follower_ids)
        return list(follower_ids - following_ids)

    def logout(self):
        self.__account.logout()

    def login(self):
        self.__account.login()

    def get_posts_by_tag(self, tags):
        self.__account.getHashtagFeed(tags)
        return self.__account.LastJson

    def get_last_json(self):
        return self.__account.LastJson

    def get_people_that_liked(self, mediaID):
        self.__account.getMediaLikers(mediaId=mediaID)
        return self.get_last_json()['users']

    def get_username_by_id(self, userID):
        self.__account.getUsernameInfo(userID)
        return self.get_last_json()['user']['username']

    def get_id_by_username(self, username):
        self.__account.searchUsername(usernameName=username)
        return self.get_last_json()['user']['pk']


def main():
    # The main is just for testing.
    import credentials
    acc = InstagramAccount(credentials.username, credentials.password)
    print(acc.get_username_by_id("7306452531"))
    acc.logout()


if __name__ == '__main__':
    main()