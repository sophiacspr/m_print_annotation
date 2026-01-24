import re
from typing import List, Dict

from controller.interfaces import IController
from model.interfaces import ITagModel
from model.tag_model import TagModel
from utils.interfaces import ITagProcessor


class TagProcessor(ITagProcessor):
    """
    Handles the transformation of tag objects to strings and vice versa,
    and performs string operations on the document text.
    """

    def __init__(self, controller: IController):
        self._controller: IController = controller

    def insert_tag_into_text(self, text: str, tag_model: ITagModel) -> str:
        """
        Inserts a single tag as a string into the specified text using an ITagModel instance.

        Args:
            text (str): The document text where the tag should be inserted.
            tag_model (ITagModel): An instance of ITagModel containing the tag data to insert.
                Required properties:
                    - position (int): The index in the text where the tag should be inserted.
                    - text (str): The text content of the tag.
                    - tag_type (str): The type of the tag.
                    - attributes (Dict[str, str]): A dictionary of attribute name-value pairs for the tag.

        Returns:
            str: The updated text with the tag inserted at the specified position.

        Raises:
            ValueError: If the text at the specified position does not match the tag's text.
        """
        position = tag_model.get_position()
        tag_text = tag_model.get_text()

        # Validate if the text at the position matches the tag text
        if text[position:position + len(tag_text)] != tag_text:
            raise ValueError(
                f"Text at position {position} does not match the provided tag text.")

        # Convert the tag to a string representation
        full_tag = str(tag_model)

        # Replace the original text with the tag at the specified position
        updated_text = text[:position] + full_tag + \
            text[position + len(tag_text):]

        return updated_text
    
    def _insert_tag_into_plain_text(self, plain_text: str, tag: ITagModel) -> str:
        """
        Inserts a tag into the plain text at the specified plain position.

        Args:
            plain_text (str): The plain text without tags.
            tag (ITagModel): An instance of ITagModel containing the tag data to insert.
                Required properties:
                    - plain_position (int): The index in the plain text where the tag should be inserted.
                    - text (str): The text content of the tag.
                    - tag_type (str): The type of the tag.
                    - attributes (Dict[str, str]): A dictionary of attribute name-value pairs for the tag.

        Returns:
            str: The updated text with the tag inserted at the specified plain position.

        Raises:
            ValueError: If the plain position is invalid.
        """
        plain_position = tag.get_plain_position()
        if plain_position is None or plain_position > len(plain_text):
            raise ValueError(
                f"Invalid plain_position for tag: {tag}")

        # Convert the tag to a string representation
        full_tag = str(tag)
        offset = len(tag.get_text())

        # Insert the tag into the plain text
        updated_text = plain_text[:plain_position] + full_tag + plain_text[plain_position+offset:]

        return updated_text

    def delete_tag_from_text(self, tag: ITagModel, text: str) -> str:
        """
        Removes a tag from the specified text based on the provided ITagModel instance.

        Args:
            tag (ITagModel): An instance of ITagModel representing the tag to remove.
            text (str): The document text containing the tag.

        Returns:
            str: The updated text with the specified tag removed.

        Raises:
            ValueError: If the specified tag is not found in the text.
        """
        tag_str = str(tag)  # Convert the tag to its string representation
        position = tag.get_position()

        # Validate if the tag exists at the expected position
        if text[position:position + len(tag_str)] != tag_str:
            raise ValueError(
                f"Tag not found at the specified position: {position}")

        # Remove the tag from the text
        updated_text = text[:position] + \
            tag.get_text() + text[position + len(tag_str):]

        return updated_text

    def update_tag(self, text: str, tag: ITagModel) -> str:
        """
        Updates a tag in the text at its specified position by replacing it with the new tag representation.

        This method locates an existing tag in the text at the given position using regex and replaces it with
        the new string representation of the provided tag.

        Args:
            text (str): The full document text containing the tag.
            tag (ITagModel): The updated tag instance that should replace the existing one.

        Returns:
            str: The updated text with the modified tag.

        Raises:
            ValueError: If no valid tag is found at the specified position.
        """
        # Get the tag position in the text
        position = tag.get_position()

        # Regex pattern to find an XML-like tag at the given position
        pattern = r'<\w+\s*[^>]*>.*?</\w+>'

        # Attempt to find a tag starting at or after the given position
        match = re.search(pattern, text[position:])
        if not match:
            raise ValueError(
                f"No valid tag found at the specified position {position}.")

        # Replace the old tag with the new tag string representation
        start_index = position + match.start(0)
        end_index = position + match.end(0)
        updated_text = text[:start_index] + str(tag) + text[end_index:]

        return updated_text

    def _extract_tags_from_text(self, text: str) -> List[Dict]:
        """
        Extracts all tags from the given text and returns them as a list of dictionaries.

        This method identifies tags in the text based on their XML-like structure, including their type,
        attributes, position, and content. It parses the tag type, attributes, and the inner text of each
        tag, while also recording the start position of each tag in the text.

        Args:
            text (str): The input text containing tags.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary represents a tag with the following keys:
                - "tag_type" (str): The type of the tag (e.g., "TIMEX3").
                - "attributes" (Dict[str, str]): A dictionary mapping attribute names to their values.
                - "position" (int): The starting position of the tag in the text.
                - "text" (str): The content enclosed within the tag.
        """
        tag_pattern = re.compile(
            r'<(?P<tag_type>\w+)\s*(?P<attributes>[^>]*)>(?P<content>.*?)</\1>',
            re.DOTALL
        )
        attribute_pattern = re.compile(r'(?P<key>\w+)="(?P<value>[^"]*)"')

        tags = []
        for match in tag_pattern.finditer(text):
            tag_type = match.group("tag_type")
            attributes_raw = match.group("attributes")
            content = match.group("content")
            start_position = match.start()

            id_name = self._controller.get_id_name(tag_type)
            if not id_name:
                #if a tag type found in the text is not defined in the current project configuration, skip it
                continue

            # Parse attributes into a dictionary
            attributes = dict(attribute_pattern.findall(attributes_raw))
            attributes["id"] = attributes.pop(id_name)

            # Extract reference keys from controller
            ref_keys = self._controller.get_id_refs(tag_type)

            # Extract references from attributes
            references = {
                key: value for key, value in attributes.items() if key in ref_keys
            }

            # Construct tag_data
            tag_data = {
                "tag_type": tag_type,
                "attributes": attributes,
                "position": start_position,
                "text": content.strip(),
                "id_name": id_name,
                "references": references
            }
            tags.append(tag_data)
        return tags

    def delete_all_tags_from_text(self, text: str) -> str:
        """
        Removes all tags from the given text, replacing them with their enclosed content.

        This method identifies and removes XML-like tags from the text, ensuring that only the content
        between the opening and closing tags remains.

        Args:
            text (str): The input text containing tags.

        Returns:
            str: The text with all tags removed, keeping only the inner content.
        """
        tag_pattern = re.compile(
            r'<(?P<tag_type>\w+)\s*(?P<attributes>[^>]*)>(?P<content>.*?)</\1>',
            re.DOTALL
        )

        return re.sub(tag_pattern, lambda match: match.group("content"), text)

    def extract_plain_text(self, text: str) -> str:
        """
        Extracts the plain text from the given text by removing all tags.

        This method uses the delete_all_tags_from_text method to remove all XML-like tags
        and return only the enclosed content.

        Args:
            text (str): The input text containing tags.

        Returns:
            str: The plain text with all tags removed.
        """
        return self.delete_all_tags_from_text(text)

    def get_plain_text_and_tags(self, text: str, tags:list[dict]=None) -> Dict[str, any]:
        """
        Extracts both the plain text and the list of tags from the given text.

        This method first extracts all tags using extract_tags_from_text, then removes all tags
        to get the plain text using delete_all_tags_from_text.

        Args:
            text (str): The input text containing tags.
            tags (list[dict], optional): Pre-extracted list of tag dictionaries. If provided,
                                        this list will be used instead of extracting tags from the text.
        Returns:
            Dict[str, any]: A dictionary with "plain_text" (str) and "tags" (List[Dict]).
        """
        plain_text = self.extract_plain_text(text)
        if tags:
            tags=self._add_plain_positions_to_tags(tags, text, plain_text)
        else:
            #todo check if this works correctly
            tags = self._extract_tags_from_text(text)
            tags = self._add_plain_positions_to_tags(tags, text, plain_text)
        return {"plain_text": plain_text, "tags": tags}
    
    def merge_plain_text_and_tags(self, plain_text: str, tags: List[Dict]) -> str:
        """
        Merges plain text and a list of tags back into a single text with tags.

        This method reinserts tags into the plain text at their specified positions.

        Args:
            plain_text (str): The plain text without tags.
            tags (List[Dict]): A list of tag dictionaries to insert into the text.
        Returns:
            str: The merged text with tags inserted.
        """
        # Sort tags by their plain_position in descending order
        sorted_tags = sorted(
            tags, key=lambda tag: tag.get("plain_position", 0), reverse=True)

        merged_text = plain_text
        for tag in sorted_tags:
            tag_model=TagModel(tag)
            merged_text = self._insert_tag_into_plain_text(merged_text, tag_model)
        return merged_text
    
    def _add_plain_positions_to_tags(self, tags: List[Dict], original_text: str, plain_text: str) -> List[Dict]:
        """
        Adds plain_position to each tag dict, indicating the start index of the tag's inner text in plain_text.

        Args:
            tags (List[Dict]): List of tag dictionaries from extract_tags_from_text.
            original_text (str): The original text with tags.
            plain_text (str): The plain text with tags removed.

        Returns:
            List[Dict]: The tags list with added "plain_position" key for each tag.
        """
        mapping = self._build_index_mapping(original_text)
        for tag in tags:
            tag_type = tag.get("tag_type")
            position = tag.get("position")
            if not tag_type or position is None or position >= len(original_text):
                tag["plain_position"] = None
                continue
            # Find content_start: after the first '>' from position
            start_search = original_text.find('>', position)
            if start_search == -1:
                tag["plain_position"] = None
                continue
            content_start = start_search + 1
            # Find raw_content_end: position of '<' in "</{tag_type}>"
            closing_tag = f"</{tag_type}>"
            end_search = original_text.find(closing_tag, content_start)
            if end_search == -1:
                tag["plain_position"] = None
                continue
            raw_content_end = end_search
            raw_content = original_text[content_start:raw_content_end]
            leading_ws = len(raw_content) - len(raw_content.lstrip())
            adjusted_content_start = content_start + leading_ws
            if adjusted_content_start < len(mapping):
                tag["plain_position"] = mapping[adjusted_content_start]
            else:
                tag["plain_position"] = None
        return tags

    def _build_index_mapping(self, original_text: str) -> List[int]:
        """
        Builds a mapping from original_text indices to plain_text indices.

        Returns a list where index i contains the plain_text index for original_text[i],
        or -1 if original_text[i] is part of markup.
        """
        mapping = [-1] * len(original_text)
        plain_idx = 0
        i = 0
        while i < len(original_text):
            if original_text[i] == '<':
                # Find the end of the tag
                end = original_text.find('>', i)
                if end != -1:
                    i = end + 1  # Skip the entire tag
                else:
                    i += 1  # Malformed, skip char
            else:
                mapping[i] = plain_idx
                plain_idx += 1
                i += 1
        return mapping

    def remove_ids_from_tags(self, text: str) -> str:
        """
        Removes ID and IDREF attributes from all tags in the given text.

        Args:
            text (str): The input text containing tags.

        Returns:
            str: The text with the tags where ID and IDREF attributes have been removed.
        """
        # Regex pattern to extract tag type, attributes, and content
        tag_pattern = re.compile(
            r'<(?P<tag_type>\w+)\s*(?P<attributes>[^>]*)>(?P<content>.*?)</\1>',
            re.DOTALL
        )
        attribute_pattern = re.compile(r'(?P<key>\w+)="(?P<value>[^"]*)"')

        # Process each tag match
        def clean_tag(match):
            tag_type = match.group("tag_type")
            attributes_raw = match.group("attributes")
            content = match.group("content")

            # Retrieve the attribute names to be removed
            idrefs = self._controller.get_id_refs(tag_type)

            # Parse attributes and remove ID and IDREF attributes
            attributes = attribute_pattern.findall(attributes_raw)
            cleaned_attributes = [
                f'{key}="{value}"' for key, value in attributes if key not in idrefs
            ]

            # Construct the cleaned tag
            cleaned_tag = f'<{tag_type} {" ".join(cleaned_attributes)}>{content}</{tag_type}>'

            return cleaned_tag

        # Substitute tags in the text with cleaned versions
        cleaned_text = tag_pattern.sub(clean_tag, text)

        return cleaned_text

    def is_sentence_unmergable(self, sentence: str) -> bool:
        """
        Checks whether the given sentence contains any tags that reference other tags.

        A sentence is considered "unmergable" if at least one tag within it has reference attributes
        (as defined by the controller's get_id_refs method).

        Args:
            sentence (str): The sentence to be analyzed.

        Returns:
            bool: True if the sentence contains referencing tags; False otherwise.
        """
        # Extract all tags from the sentence
        tags = self._extract_tags_from_text(sentence)

        # Check if any tag contains references
        for tag_data in tags:
            references = tag_data.get("references", {})
            if references:
                return True

        return False
