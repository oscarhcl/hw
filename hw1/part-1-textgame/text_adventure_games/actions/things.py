from . import base
from . import preconditions as P
from .consume import Drink, Eat
from .rose import Smell_Rose


class Get(base.Action):
    ACTION_NAME = "get"
    ACTION_DESCRIPTION = "Get something and add it to the inventory"
    ACTION_ALIASES = ["take"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        self.item = self.parser.match_item(command, self.location.items)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The item must be matched.
        * The character must be at the location
        * The item must be at the location
        * The item must be gettable
        """
        if not self.was_matched(self.item, "I don't see it."):
            message = "I don't see it."
            self.parser.fail(message)
            return False
        if not self.location.here(self.character):
            message = "{name} is not here.".format(name=self.character.name)
            self.parser.fail(message)
            return False
        if not self.location.here(self.item):
            message = "There is no {name} here.".format(name=self.item.name)
            self.parser.fail(message)
            return False
        if not self.item.get_property("gettable"):
            error_message = "{name} is not {property_name}.".format(
                name=self.item.name.capitalize(), property_name="gettable"
            )
            self.parser.fail(error_message)
            return False
        return True

    def apply_effects(self):
        """
        Get's an item from the location and adds it to the character's
        inventory, assuming preconditions are met.
        """
        self.location.remove_item(self.item)
        self.character.add_to_inventory(self.item)
        description = "{character_name} got the {item_name}.".format(
            character_name=self.character.name, item_name=self.item.name
        )
        self.parser.ok(description)


class Drop(base.Action):
    ACTION_NAME = "drop"
    ACTION_DESCRIPTION = "Drop something from the character's inventory"
    ACTION_ALIASES = ["toss", "get rid of"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        self.item = self.parser.match_item(command, self.character.inventory)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The item must be in the character's inventory
        """
        if not self.was_matched(self.item, "I don't see it."):
            return False
        if not self.character.is_in_inventory(self.item):
            d = "{character_name} does not have the {item_name}."
            description = d.format(
                character_name=self.character.name, item_name=self.item.name
            )
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        """
        Drop removes an item from character's inventory and adds it to the
        current location, assuming preconditions are met
        """
        self.character.remove_from_inventory(self.item)
        self.item.location = self.location
        self.location.add_item(self.item)
        d = "{character_name} dropped the {item_name} in the {location}."
        description = d.format(
            character_name=self.character.name.capitalize(),
            item_name=self.item.name,
            location=self.location.name,
        )
        self.parser.ok(description)


class Inventory(base.Action):
    ACTION_NAME = "inventory"
    ACTION_DESCRIPTION = "Check the character's inventory"
    ACTION_ALIASES = ["i"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        if self.character is None:
            return False
        return True

    def apply_effects(self):
        if len(self.character.inventory) == 0:
            description = f"{self.character.name}'s inventory is empty."
            self.parser.ok(description)
        else:
            description = f"{self.character.name}'s inventory contains:\n"
            for item_name in self.character.inventory:
                item = self.character.inventory[item_name]
                description += "* {item}\n".format(item=item.description)
            self.parser.ok(description)


class Examine(base.Action):
    ACTION_NAME = "examine"
    ACTION_DESCRIPTION = "Examine an item"
    ACTION_ALIASES = ["look at", "x"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.matched_item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        if self.character is None:
            return False
        return True

    def apply_effects(self):
        """The player wants to examine an item"""
        if self.matched_item:
            if self.matched_item.examine_text:
                self.parser.ok(self.matched_item.examine_text)
            else:
                self.parser.ok(self.matched_item.description)
        else:
            self.parser.ok("You don't see anything special.")


class Give(base.Action):
    ACTION_NAME = "give"
    ACTION_DESCRIPTION = "Give something to someone"
    ACTION_ALIASES = ["hand"]

    def __init__(self, game, command: str):
        super().__init__(game)
        give_words = ["give", "hand"]
        command_before_word = ""
        command_after_word = command
        for word in give_words:
            if word in command:
                parts = command.split(word, 1)
                command_before_word = parts[0]
            command_after_word = parts[1]
            break
        self.giver = self.parser.get_character(command_before_word)
        self.recipient = self.parser.get_character(command_after_word)
        self.item = self.parser.match_item(command, self.giver.inventory)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The item must be in the giver's inventory
        * The character must be at the same location as the recipient
        """
        if not self.was_matched(self.item, "I don't see it."):
            return False
        if not self.giver.is_in_inventory(self.item):
            return False
        if not self.giver.location.here(self.recipient):
            return False
        return True

    def apply_effects(self):
        """
        Drop removes an item from character's inventory and adds it to the
        current location. (Assumes that the preconditions are met.)
        If the recipient is hungry and the item is food, the recipient will
        eat it.
        If the recipient is thisty and the item is drink, the recipient will
        drink it.
        """
        self.giver.remove_from_inventory(self.item)
        self.recipient.add_to_inventory(self.item)
        description = "{giver} gave the {item_name} to {recipient}".format(
            giver=self.giver.name.capitalize(),
            item_name=self.item.name,
            recipient=self.recipient.name.capitalize(),
        )
        self.parser.ok(description)

        if self.recipient.get_property("is_hungry") and self.item.get_property(
            "is_food"
        ):
            command = "{name} eat {food}".format(
                name=self.recipient.name, food=self.item.name
            )
            eat = Eat(self.game, command)
            eat()

        if self.recipient.get_property("is_thisty") and self.item.get_property(
            "is_drink"
        ):
            command = "{name} drink {drink}".format(
                name=self.recipient.name, drink=self.item.name
            )
            drink = Drink(self.game, command)
            drink()

        if self.item.get_property("scent"):
            command = "{name} smell {thing}".format(
                name=self.recipient.name, thing=self.item.name
            )
            smell = Smell_Rose(self.game, command)
            smell()


class Unlock_Door(base.Action):
    ACTION_NAME = "unlock door"
    ACTION_DESCRIPTION = "Unlock a door"

    def __init__(self, game, command):
        super().__init__(game)
        self.command = command
        self.character = self.parser.get_character(command)
        self.key = self.parser.match_item(
            "key", self.parser.get_items_in_scope(self.character)
        )
        self.door = self.parser.match_item(
            "door", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        if self.door and self.door.get_property("is_locked") and self.key:
            return True
        else:
            return False

    def apply_effects(self):
        self.door.set_property("is_locked", False)
        self.parser.ok("Door is unlocked")


class Read_Runes(base.Action):
    ACTION_NAME = "read runes"
    ACTION_DESCRIPTION = "Read runes off of the candle"

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.candle = self.parser.match_item(
            "candle", self.parser.get_items_in_scope(self.character)
        )
        self.ghost = self.character.location.characters.get("ghost")

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.candle, "There is no candle here."):
            return False
        if not self.is_in_inventory(self.character, self.candle):
            return False
        if not self.was_matched(self.ghost, "There is nothing here to banish."):
            return False
        if not self.candle.get_property("is_lit"):
            self.parser.fail("The candle must be lit first.")
            return False
        return True

    def apply_effects(self):
        self.ghost.set_property("is_banished", True)
        self.parser.ok("The runes flare and the ghost is banished.")
        items = list(self.ghost.inventory.keys())
        for item_name in items:
            item = self.ghost.inventory[item_name]
            command = "{ghost} drop {item}".format(
                ghost=self.ghost.name, item=item.name
            )
            drop = Drop(self.game, command)
            if drop.check_preconditions():
                drop.apply_effects()
        self.ghost.location.remove_character(self.ghost)


class Propose(base.Action):
    ACTION_NAME = "propose"
    ACTION_DESCRIPTION = "Propose marriage to someone"

    def __init__(self, game, command):
        super().__init__(game)
        command_before_word, command_after_word = self.parser.split_command(
            command, "propose"
        )
        self.proposer = self.parser.get_character(command_before_word)
        self.propositioned = self.parser.get_character(command_after_word)

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.proposer):
            return False
        if not self.was_matched(self.propositioned, "Nobody hears the proposal."):
            return False
        if self.proposer.location != self.propositioned.location:
            self.parser.fail("They need to be together for that.")
            return False
        if self.proposer.get_property("is_married"):
            self.parser.fail("{name} is already married.".format(name=self.proposer.name))
            return False
        if self.propositioned.get_property("is_married"):
            self.parser.fail(
                "{name} is already married.".format(name=self.propositioned.name)
            )
            return False
        if self.proposer.get_property("emotional_state") != "happy":
            self.parser.fail("{name} is not feeling happy enough.".format(name=self.proposer.name))
            return False
        if self.propositioned.get_property("emotional_state") != "happy":
            self.parser.fail(
                "{name} is not feeling happy enough.".format(
                    name=self.propositioned.name
                )
            )
            return False
        return True

    def apply_effects(self):
        self.proposer.set_property("is_married", True)
        self.propositioned.set_property("is_married", True)
        if self.proposer.get_property("is_royal") or self.propositioned.get_property(
            "is_royal"
        ):
            self.proposer.set_property("is_royal", True)
            self.propositioned.set_property("is_royal", True)
        self.parser.ok(
            "{proposer} proposes to {propositioned}. They are married.".format(
                proposer=self.proposer.name.capitalize(),
                propositioned=self.propositioned.name.capitalize(),
            )
        )


class Wear_Crown(base.Action):
    ACTION_NAME = "wear crown"
    ACTION_DESCRIPTION = "Put a crown in your inventory atop your head"

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.crown = self.parser.match_item(
            "crown", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.crown, "There is no crown here."):
            return False
        if not self.is_in_inventory(self.character, self.crown):
            return False
        if not self.character.get_property("is_royal"):
            self.parser.fail("{name} is not royal.".format(name=self.character.name))
            return False
        return True

    def apply_effects(self):
        self.character.set_property("is_crowned", True)
        self.crown.set_property("is_worn", True)
        self.parser.ok("{name} wears the crown.".format(name=self.character.name.capitalize()))


class Sit_On_Throne(base.Action):
    ACTION_NAME = "sit on throne"
    ACTION_DESCRIPTION = "Sit on the throne, if you are royalty"

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.throne = self.parser.match_item("throne", self.character.location.items)

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.throne, "There is no throne here."):
            return False
        if not self.character.get_property("is_crowned"):
            self.parser.fail("{name} is not crowned.".format(name=self.character.name))
            return False
        return True

    def apply_effects(self):
        self.character.set_property("is_reigning", True)
        self.parser.ok(
            "{name} sits on the throne and begins to reign.".format(
                name=self.character.name.capitalize()
            )
        )
