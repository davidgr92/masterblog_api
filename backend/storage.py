import json
from os.path import isfile


class StorageJson:
    def __init__(self, file_path):
        self._file_path = file_path
        if not isfile(file_path):
            self.save_to_json({
                "toc": {},
                "posts": []
            })

    def save_to_json(self, data):
        """Saves the provided data to the json data file"""
        with open(self._file_path, 'w') as file:
            file.write(json.dumps(data, indent=4))

    def list_posts(self) -> dict:
        """Returns a dictionary of dictionaries that
        contains the posts data in the database.
        The function loads the information from the JSON
        file and returns the data."""
        with open(self._file_path, 'r') as file:
            return json.loads(file.read())

    def find_post_by_id(self, post_id) -> dict:
        """Return post object based on provided id."""
        all_data = self.list_posts()
        posts_list = all_data['posts']
        posts_toc = all_data['toc']

        post_index = posts_toc[str(post_id)]
        return posts_list[post_index]

    def add_post(self, post_dict) -> None:
        """Adds a new post to the posts storage file.
        Loads the information from the JSON file, adds the new post data,
        and saves it. The function doesn't validate the input.
        """
        all_data = self.list_posts()
        posts_list = all_data['posts']
        posts_toc = all_data['toc']

        posts_list.append(post_dict)
        new_id = str(post_dict['id'])
        new_index = posts_list.index(post_dict)
        posts_toc.update({new_id: new_index})

        self.save_to_json(all_data)

    def delete_post(self, post_id) -> None:
        """Deletes a post from the posts storage file.
        Loads the information from the JSON file, deletes the post by id,
        and saves it. The function doesn't validate the input.
        """
        all_data = self.list_posts()
        posts_list = all_data['posts']
        posts_toc = all_data['toc']

        post_index = posts_toc[str(post_id)]
        del posts_list[post_index]  # Delete post object
        del all_data['toc'][str(post_id)]  # Delete post from toc

        # Update indexes in following object in toc
        keys_to_update = [key for key in all_data['toc']
                          if int(key) > post_id]
        for key in keys_to_update:
            all_data['toc'][key] -= 1

        self.save_to_json(all_data)

    def update_post(self, post_id, post_dict):
        """Updates a post from the posts storage file.
        Loads the information from the JSON file, updates the post,
        and saves it. The function doesn't validate the input.
        """
        all_data = self.list_posts()
        posts_list = all_data['posts']
        posts_toc = all_data['toc']

        post_index = posts_toc[str(post_id)]
        posts_list[post_index].update(post_dict)

        self.save_to_json(all_data)
