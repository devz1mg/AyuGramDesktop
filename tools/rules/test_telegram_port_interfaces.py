"""Lightweight source-contract checks; these do not replace a C++ build."""

from pathlib import Path
import re
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "Telegram" / "SourceFiles"


class TelegramPortInterfaceTests(unittest.TestCase):
    def test_windows_application_links_dns_api(self):
        cmake = (SOURCE.parent / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIsNotNone(
            re.search(
                r"if \(WIN32\)\s+target_link_libraries\(Telegram PRIVATE dnsapi\)",
                cmake,
            ),
            "Static Qt Network DNS lookup requires the Windows DNS import library",
        )

    def test_custom_forward_paths_return_a_message_id_value(self):
        api = (SOURCE / "apiwrap.cpp").read_text(encoding="utf-8")
        custom_paths = api.split("FullMsgId ApiWrap::forwardMessages(", 1)[1].split(
            "auto &histories", 1
        )[0]
        self.assertIn("AyuForward::forwardMessages", custom_paths)
        self.assertIn("AyuForward::intelligentForward", custom_paths)
        self.assertNotRegex(
            custom_paths,
            r"\breturn\s*;",
            "Custom forwarding has no synchronous local ID and must return an empty FullMsgId",
        )

    def test_link_info_includes_admin_rights_definition(self):
        header = (SOURCE / "window/window_session_controller_link_info.h").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            '#include "data/data_chat_participant_status.h"',
            header.split("struct PeerByLinkInfo", 1)[0],
            "PeerByLinkInfo must not rely on incidental includes for ChatAdminRights",
        )

    def test_ayu_menu_icons_exist_in_current_styles(self):
        available = set()
        for path in SOURCE.rglob("*.style"):
            available.update(re.findall(
                r"^\s*(menuIcon\w+)\s*:",
                path.read_text(encoding="utf-8"),
                re.M,
            ))
        self.assertTrue(available, "No menu icon definitions found")
        unknown = []
        for path in (SOURCE / "ayu").rglob("*"):
            if path.suffix not in {".cpp", ".h", ".mm"}:
                continue
            used = set(re.findall(
                r"\bst::(menuIcon\w+)\b", path.read_text(encoding="utf-8")
            ))
            unknown.extend(
                f"{path.relative_to(SOURCE)}: {icon}"
                for icon in sorted(used - available)
            )
        self.assertEqual(unknown, [], "AyuGram must use current menu icon names")

    def test_ayu_localization_keys_exist_in_current_catalog(self):
        catalog = (SOURCE.parent / "Resources/langs/lang.strings").read_text(
            encoding="utf-8"
        )
        available = set(re.findall(
            r'^"(\w+)(?:#[^\"]+)?"\s*=', catalog, re.M
        ))
        self.assertTrue(available, "No language keys found")
        unknown = []
        for path in (SOURCE / "ayu").rglob("*"):
            if path.suffix not in {".cpp", ".h", ".mm"}:
                continue
            used = set(re.findall(
                r"\btr::((?:lng_|ayu_)\w+)\b", path.read_text(encoding="utf-8")
            ))
            unknown.extend(
                f"{path.relative_to(SOURCE)}: {key}"
                for key in sorted(used - available)
            )
        self.assertEqual(unknown, [], "AyuGram must use current localization keys")

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
