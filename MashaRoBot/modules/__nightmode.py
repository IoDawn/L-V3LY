from MashaRoBot.modules.sql.night_mode_sql import add_nightmode, rmnightmode, get_all_chat_id, is_nightmode_indb
from telethon.tl.types import ChatBannedRights
from apscheduler.schedulers.asyncio import AsyncIOScheduler 
from telethon import functions
from MashaRoBot.events import register
from MashaRoBot import telethn, OWNER_ID
import os
from telethon import *
from telethon import Button, custom, events
hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)
openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChatAdminRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
)
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await telethn(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True

async def can_change_info(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )

@register(pattern="^/(nightmode|Nightmode|NightMode) ?(.*)")
async def profanity(event):
    
    if not event.is_group:
        await event.reply("Anda Hanya Dapat Menonton Nsfw di Grup.")
        return
    input_str = event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID):
        await event.reply("`Saya Harus Menjadi Admin Untuk Melakukan Ini!`")
        return
    if await is_admin(event, event.message.sender_id):
        if (
            input_str == "on"
            or input_str == "On"
            or input_str == "ON"
            or input_str == "enable"
        ):
            if is_nightmode_indb(str(event.chat_id)):
                await event.reply("Obrolan Ini Sudah Diaktifkan Mode Malam.")
                return
            add_nightmode(str(event.chat_id))
            await event.reply(
                f"**Menambahkan Obrolan {event.chat.title} dan Id {event.chat_id} ke dalam database. Grup Ini Akan Ditutup Pada Pukul 12 Malam(WIB) Dan Akan Dibuka Kembali Pada Pukul 06 Pagi(WIB)**"
            )
        elif (
            input_str == "off"
            or input_str == "Off"
            or input_str == "OFF"
            or input_str == "disable"
        ):

            if not is_nightmode_indb(str(event.chat_id)):
                await event.reply("Obrolan Ini Belum Mengaktifkan Mode Malam.")
                return
            rmnightmode(str(event.chat_id))
            await event.reply(
                f"**Menghapus obrolan {event.chat.title} dan id {event.chat_id} dari database. Grup Ini Tidak Akan Ditutup Lagi Pada Pukul 12 Malam(WIB) Dan Seterusnya**"
            )
        else:
            await event.reply("Saya hanya mengerti `/nightmode on` dan `/nightmode off`")
    else:
        await event.reply("`Anda Harus Menjadi Admin Untuk Melakukan Ini!`")
        return


async def job_close():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                "`Sudah jam 12:00 Malam, Grup Ditutup Sampai Jam 6 Pagi. Mode Malam Dimulai!` \n**Didukung oleh @admin**",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=hehes
                )
            )
            if CLEAN_GROUPS:
                async for user in tbot.iter_participants(int(warner.chat_id)):
                    if user.deleted:
                        await tbot.edit_permissions(
                            int(warner.chat_id), user.id, view_messages=False
                        )
        except Exception as e:
            print(f"Tidak Dapat Menutup Grup {warner} - {e}")


scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=55)
scheduler.start()


async def job_open():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                "`Jam 06:00 pagi, Grup kembali Dibuka.`\n**Didukung oleh @admin**",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=openhehe
                )
            )
        except Exception as e:
            print(f"Tidak Dapat Membuka Grup {warner.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(job_open, trigger="cron", hour=6, minute=10)
scheduler.start()


__help__ = """
<b> Mode Malam </b>
Tutup grup Anda pada pukul 12.00 dan buka kembali pada pukul 6.00(WIB)
<i> Hanya tersedia untuk negara-negara Asia </i>

- /nightmode [ON/OFF]: Aktifkan/Nonaktifkan Mode Malam.

"""
__mod_name__ = "Night 🌒"
