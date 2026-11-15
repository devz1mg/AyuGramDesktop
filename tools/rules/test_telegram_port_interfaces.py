"""Lightweight source-contract checks; these do not replace a C++ build."""

from pathlib import Path
import re
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "Telegram" / "SourceFiles"


class TelegramPortInterfaceTests(unittest.TestCase):
    def test_inline_bot_helpers_cover_inline_message_constructors(self):
        scheme = (SOURCE / "mtproto/scheme/api.tl").read_text(encoding="utf-8")
        constructors = re.findall(
            r"^(\w+)#[0-9a-f]+[^\n]* = BotInlineMessage;", scheme, re.M
        )
        self.assertTrue(constructors, "No inline message constructors found")
        required = {"MTPD" + name for name in constructors}
        helper = (SOURCE / "ayu/utils/telegram_helpers.cpp").read_text(
            encoding="utf-8"
        )
        visitors = helper.split("const auto text = message->match(")[1:]
        self.assertTrue(visitors, "No inline message visitors found")
        for index, body in enumerate(visitors, start=1):
            with self.subTest(visitor=index):
                visitor = body.split("if (text.isEmpty()", 1)[0]
                handled = set(re.findall(r"const (MTPD\w+)\s*&", visitor))
                self.assertEqual(
                    required - handled,
                    set(),
                    "Inline bot helpers must handle every BotInlineMessage constructor",
                )

    def test_message_flag_references_exist_in_current_enum(self):
        types = (SOURCE / "data/data_types.h").read_text(encoding="utf-8")
        definition = re.search(
            r"enum class MessageFlag\s*:\s*\w+\s*\{(.*?)\};", types, re.S
        )
        self.assertIsNotNone(definition, "MessageFlag enum not found")
        available = set(re.findall(r"^\s*(\w+)\s*=", definition.group(1), re.M))
        self.assertTrue(available, "No message flags found; update the source probe")
        unknown = []
        references = 0
        for path in SOURCE.rglob("*"):
            if path.suffix not in {".cpp", ".h", ".mm"}:
                continue
            source = path.read_text(encoding="utf-8")
            used = set(re.findall(r"\bMessageFlag::(\w+)", source))
            references += len(used)
            unknown.extend(
                f"{path.relative_to(SOURCE)}: {name}"
                for name in sorted(used - available)
            )
        self.assertGreater(references, 0, "No message flag references found")
        self.assertEqual(unknown, [], "MessageFlag references must match the enum")

    def test_message_history_covers_element_delegate_pure_virtuals(self):
        delegate = (SOURCE / "history/view/history_view_element.h").read_text(
            encoding="utf-8"
        )
        delegate = delegate.split("class ElementDelegate {", 1)[1].split(
            "virtual ~ElementDelegate", 1
        )[0]
        required = set(re.findall(
            r"virtual[^;{]*?\b(element\w+)\s*\([^;{]*\)\s*=\s*0\s*;",
            delegate,
        ))
        self.assertTrue(required, "No delegate methods found; update the source probe")
        history = (SOURCE / "ayu/ui/message_history/history_inner.h").read_text(
            encoding="utf-8"
        )
        overrides = set(re.findall(
            r"\b(element\w+)\s*\([^;{]*\)\s*override\s*;", history
        ))
        self.assertEqual(
            required - overrides,
            set(),
            "AyuGram message history must implement every pure virtual delegate method",
        )

    def test_donation_currency_icon_uses_current_upstream_api(self):
        icons = (SOURCE / "info/channel_statistics/earn/earn_icons.h").read_text(
            encoding="utf-8"
        )
        available = set(re.findall(r"\b(IconCurrency\w+)\s*\(", icons))
        self.assertTrue(available, "No icon API found; update the source probe")
        donation = (SOURCE / "ayu/ui/boxes/donate_info_box.cpp").read_text(
            encoding="utf-8"
        )
        used = set(re.findall(r"Ui::Earn::(IconCurrency\w+)\s*\(", donation))
        self.assertTrue(used, "No donation currency icon found; update the probe")
        self.assertEqual(
            used - available,
            set(),
            "The donation box must use currency icons declared by upstream",
        )


if __name__ == "__main__":
    unittest.main()
