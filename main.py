#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Telegram Nomor Virtual
Mengirim nomor virtual random ke user
Service: OnlineSim.io
Versi: 2.8 (Enhanced with Auto Prayer Notifications)
"""

import random
import time
import telebot
import phonenumbers
import json
import os
import requests
import threading
from datetime import datetime, timedelta
from threading import Lock
from functools import wraps

from src import utils
from src.utils import User
from src.vneng import VNEngine
from telebot import types

# ==================== KONFIGURASI ====================

# URL Gambar Bot - GANTI DENGAN LINK GAMBAR KAMU
BANNER_IMAGE_URL = "https://files.catbox.moe/2fhgi4.jpg"

# ADMIN/OWNER USER ID - GANTI DENGAN USER ID TELEGRAM KAMU
OWNER_ID = 7804463533  # Ganti dengan user ID Telegram kamu

# Developer Info
DEVELOPER = "@Jeeyhosting"

# File database untuk menyimpan user
DATABASE_FILE = "database.json"

# Lock untuk database access
db_lock = Lock()

# Storage untuk broadcast message sementara
broadcast_storage = {}

# Cache untuk mengurangi API calls
country_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 300  # 5 menit

# Prayer times cache
prayer_times_cache = {"data": None, "timestamp": 0, "date": ""}
PRAYER_CACHE_DURATION = 3600  # 1 jam

# Flag untuk prayer notification thread
prayer_notification_active = True

FLAGS = {
    # Asia
    'AF': '🇦🇫', 'AM': '🇦🇲', 'AZ': '🇦🇿', 'BH': '🇧🇭', 'BD': '🇧🇩',
    'BT': '🇧🇹', 'BN': '🇧🇳', 'KH': '🇰🇭', 'CN': '🇨🇳', 'GE': '🇬🇪',
    'HK': '🇭🇰', 'IN': '🇮🇳', 'ID': '🇮🇩', 'IR': '🇮🇷', 'IQ': '🇮🇶',
    'IL': '🇮🇱', 'JP': '🇯🇵', 'JO': '🇯🇴', 'KZ': '🇰🇿', 'KP': '🇰🇵',
    'KR': '🇰🇷', 'KW': '🇰🇼', 'KG': '🇰🇬', 'LA': '🇱🇦', 'LB': '🇱🇧',
    'MO': '🇲🇴', 'MY': '🇲🇾', 'MV': '🇲🇻', 'MN': '🇲🇳', 'MM': '🇲🇲',
    'NP': '🇳🇵', 'OM': '🇴🇲', 'PK': '🇵🇰', 'PS': '🇵🇸', 'PH': '🇵🇭',
    'QA': '🇶🇦', 'SA': '🇸🇦', 'SG': '🇸🇬', 'LK': '🇱🇰', 'SY': '🇸🇾',
    'TW': '🇹🇼', 'TJ': '🇹🇯', 'TH': '🇹🇭', 'TL': '🇹🇱', 'TR': '🇹🇷',
    'TM': '🇹🇲', 'AE': '🇦🇪', 'UZ': '🇺🇿', 'VN': '🇻🇳', 'YE': '🇾🇪',
    
    # Europe
    'AL': '🇦🇱', 'AD': '🇦🇩', 'AT': '🇦🇹', 'BY': '🇧🇾', 'BE': '🇧🇪',
    'BA': '🇧🇦', 'BG': '🇧🇬', 'HR': '🇭🇷', 'CY': '🇨🇾', 'CZ': '🇨🇿',
    'DK': '🇩🇰', 'EE': '🇪🇪', 'FI': '🇫🇮', 'FR': '🇫🇷', 'DE': '🇩🇪',
    'GR': '🇬🇷', 'HU': '🇭🇺', 'IS': '🇮🇸', 'IE': '🇮🇪', 'IT': '🇮🇹',
    'XK': '🇽🇰', 'LV': '🇱🇻', 'LI': '🇱🇮', 'LT': '🇱🇹', 'LU': '🇱🇺',
    'MT': '🇲🇹', 'MD': '🇲🇩', 'MC': '🇲🇨', 'ME': '🇲🇪', 'NL': '🇳🇱',
    'MK': '🇲🇰', 'NO': '🇳🇴', 'PL': '🇵🇱', 'PT': '🇵🇹', 'RO': '🇷🇴',
    'RU': '🇷🇺', 'SM': '🇸🇲', 'RS': '🇷🇸', 'SK': '🇸🇰', 'SI': '🇸🇮',
    'ES': '🇪🇸', 'SE': '🇸🇪', 'CH': '🇨🇭', 'UA': '🇺🇦', 'GB': '🇬🇧',
    'VA': '🇻🇦',
    
    # Africa
    'DZ': '🇩🇿', 'AO': '🇦🇴', 'BJ': '🇧🇯', 'BW': '🇧🇼', 'BF': '🇧🇫',
    'BI': '🇧🇮', 'CM': '🇨🇲', 'CV': '🇨🇻', 'CF': '🇨🇫', 'TD': '🇹🇩',
    'KM': '🇰🇲', 'CG': '🇨🇬', 'CD': '🇨🇩', 'CI': '🇨🇮', 'DJ': '🇩🇯',
    'EG': '🇪🇬', 'GQ': '🇬🇶', 'ER': '🇪🇷', 'SZ': '🇸🇿', 'ET': '🇪🇹',
    'GA': '🇬🇦', 'GM': '🇬🇲', 'GH': '🇬🇭', 'GN': '🇬🇳', 'GW': '🇬🇼',
    'KE': '🇰🇪', 'LS': '🇱🇸', 'LR': '🇱🇷', 'LY': '🇱🇾', 'MG': '🇲🇬',
    'MW': '🇲🇼', 'ML': '🇲🇱', 'MR': '🇲🇷', 'MU': '🇲🇺', 'MA': '🇲🇦',
    'MZ': '🇲🇿', 'NA': '🇳🇦', 'NE': '🇳🇪', 'NG': '🇳🇬', 'RW': '🇷🇼',
    'ST': '🇸🇹', 'SN': '🇸🇳', 'SC': '🇸🇨', 'SL': '🇸🇱', 'SO': '🇸🇴',
    'ZA': '🇿🇦', 'SS': '🇸🇸', 'SD': '🇸🇩', 'TZ': '🇹🇿', 'TG': '🇹🇬',
    'TN': '🇹🇳', 'UG': '🇺🇬', 'ZM': '🇿🇲', 'ZW': '🇿🇼',
    
    # North America
    'AG': '🇦🇬', 'BS': '🇧🇸', 'BB': '🇧🇧', 'BZ': '🇧🇿', 'CA': '🇨🇦',
    'CR': '🇨🇷', 'CU': '🇨🇺', 'DM': '🇩🇲', 'DO': '🇩🇴', 'SV': '🇸🇻',
    'GD': '🇬🇩', 'GT': '🇬🇹', 'HT': '🇭🇹', 'HN': '🇭🇳', 'JM': '🇯🇲',
    'MX': '🇲🇽', 'NI': '🇳🇮', 'PA': '🇵🇦', 'KN': '🇰🇳', 'LC': '🇱🇨',
    'VC': '🇻🇨', 'TT': '🇹🇹', 'US': '🇺🇸',
    
    # South America
    'AR': '🇦🇷', 'BO': '🇧🇴', 'BR': '🇧🇷', 'CL': '🇨🇱', 'CO': '🇨🇴',
    'EC': '🇪🇨', 'GY': '🇬🇾', 'PY': '🇵🇾', 'PE': '🇵🇪', 'SR': '🇸🇷',
    'UY': '🇺🇾', 'VE': '🇻🇪',
    
    # Oceania
    'AU': '🇦🇺', 'FJ': '🇫🇯', 'KI': '🇰🇮', 'MH': '🇲🇭', 'FM': '🇫🇲',
    'NR': '🇳🇷', 'NZ': '🇳🇿', 'PW': '🇵🇼', 'PG': '🇵🇬', 'WS': '🇼🇸',
    'SB': '🇸🇧', 'TO': '🇹🇴', 'TV': '🇹🇻', 'VU': '🇻🇺'
}

def get_flag(country_code):
    """Mengambil emoji bendera berdasarkan kode negara"""
    return FLAGS.get(country_code.upper(), '🏳️')


# ==================== PRAYER TIMES FUNCTIONS ====================

def get_prayer_times():
    """Ambil jadwal waktu sholat untuk Manado"""
    global prayer_times_cache
    
    current_time = time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Cek cache
    if (prayer_times_cache["data"] and 
        prayer_times_cache["date"] == today and
        (current_time - prayer_times_cache["timestamp"]) < PRAYER_CACHE_DURATION):
        return prayer_times_cache["data"]
    
    try:
        # API Aladhan untuk jadwal sholat Manado
        # Latitude: 1.4748, Longitude: 124.8421
        url = "http://api.aladhan.com/v1/timings"
        params = {
            "latitude": 1.4748,
            "longitude": 124.8421,
            "method": 2,  # ISNA method
            "date": today
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            timings = data['data']['timings']
            
            prayer_data = {
                "Subuh": timings['Fajr'],
                "Dzuhur": timings['Dhuhr'],
                "Ashar": timings['Asr'],
                "Maghrib": timings['Maghrib'],
                "Isya": timings['Isha']
            }
            
            # Update cache
            prayer_times_cache["data"] = prayer_data
            prayer_times_cache["timestamp"] = current_time
            prayer_times_cache["date"] = today
            
            return prayer_data
        else:
            print(f"⚠️ Error fetching prayer times: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error in get_prayer_times: {e}")
        return None


def send_prayer_notification(prayer_name, prayer_time):
    """Kirim notifikasi waktu sholat ke semua user"""
    users = get_all_users()
    
    pesan = (
        f"🕌 PENGINGAT WAKTU SHOLAT 🕌\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏰ Waktu {prayer_name}: {prayer_time}\n\n"
        f"🤲 Saatnya menunaikan sholat {prayer_name}\n"
        f"Jangan lupa berwudhu dan sholat tepat waktu!\n\n"
        f"بَارَكَ اللهُ فِيْكُمْ\n"
        f"Semoga Allah memberkahi kalian\n\n"
        f"📅 {datetime.now().strftime('%d %B %Y')}"
    )
    
    sukses = 0
    gagal = 0
    
    for user_id in users.keys():
        try:
            bot.send_message(
                chat_id=int(user_id),
                text=pesan
            )
            sukses += 1
            time.sleep(0.05)  # Delay untuk menghindari rate limit
        except Exception as e:
            print(f"⚠️ Failed to send prayer notification to {user_id}: {e}")
            gagal += 1
    
    print(f"✅ Prayer notification sent: {prayer_name} - Success: {sukses}, Failed: {gagal}")


def prayer_times_scheduler():
    """Background thread untuk mengirim notifikasi waktu sholat"""
    global prayer_notification_active
    
    print("🕌 Prayer times scheduler started")
    sent_prayers = set()  # Track prayers yang sudah dikirim hari ini
    last_date = ""
    
    while prayer_notification_active:
        try:
            current_time = datetime.now()
            current_date = current_time.strftime("%Y-%m-%d")
            current_hour_minute = current_time.strftime("%H:%M")
            
            # Reset sent_prayers setiap hari baru
            if current_date != last_date:
                sent_prayers.clear()
                last_date = current_date
                print(f"📅 New day: {current_date} - Prayer notifications reset")
            
            # Ambil jadwal sholat
            prayer_times = get_prayer_times()
            
            if prayer_times:
                for prayer_name, prayer_time in prayer_times.items():
                    prayer_time_str = prayer_time[:5]  # Ambil HH:MM saja
                    
                    # Cek apakah sekarang waktu sholat dan belum dikirim
                    key = f"{current_date}_{prayer_name}"
                    if current_hour_minute == prayer_time_str and key not in sent_prayers:
                        print(f"🕌 Sending {prayer_name} notification at {prayer_time_str}")
                        send_prayer_notification(prayer_name, prayer_time_str)
                        sent_prayers.add(key)
            
            # Cek setiap 30 detik
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Error in prayer_times_scheduler: {e}")
            time.sleep(60)  # Wait 1 minute before retry


# ==================== DECORATORS ====================

def error_handler(func):
    """Decorator untuk handle error pada handler"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"❌ Error in {func.__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Coba kirim pesan error ke user
            try:
                if args and hasattr(args[0], 'chat'):
                    bot.send_message(
                        args[0].chat.id,
                        "❌ Terjadi kesalahan sistem. Silakan coba lagi nanti."
                    )
            except:
                pass
    return wrapper


def owner_only(func):
    """Decorator untuk restrict fungsi hanya untuk owner"""
    @wraps(func)
    def wrapper(message_or_call, *args, **kwargs):
        user_id = message_or_call.from_user.id
        if user_id != OWNER_ID:
            try:
                if hasattr(message_or_call, 'message'):
                    bot.answer_callback_query(
                        message_or_call.id,
                        "❌ Unauthorized",
                        show_alert=True
                    )
                else:
                    bot.reply_to(
                        message_or_call,
                        "❌ Kamu tidak memiliki akses ke fitur ini."
                    )
            except:
                pass
            return
        return func(message_or_call, *args, **kwargs)
    return wrapper


# ==================== DATABASE FUNCTIONS ====================

def load_database():
    """Load database dari file JSON dengan thread-safe"""
    with db_lock:
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validasi struktur database
                    if not isinstance(data, dict) or "users" not in data:
                        print("⚠️ Invalid database structure, creating new")
                        return {"users": {}}
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading database: {e}")
                # Backup corrupted database
                if os.path.exists(DATABASE_FILE):
                    backup_file = f"{DATABASE_FILE}.backup.{int(time.time())}"
                    try:
                        os.rename(DATABASE_FILE, backup_file)
                        print(f"📁 Corrupted database backed up to: {backup_file}")
                    except:
                        pass
                return {"users": {}}
        return {"users": {}}


def save_database(data):
    """Simpan database ke file JSON dengan thread-safe"""
    with db_lock:
        try:
            # Validasi data sebelum save
            if not isinstance(data, dict) or "users" not in data:
                print("❌ Invalid data structure, cannot save")
                return False
            
            # Tulis ke temporary file dulu
            temp_file = f"{DATABASE_FILE}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Rename ke file asli (atomic operation)
            os.replace(temp_file, DATABASE_FILE)
            return True
        except IOError as e:
            print(f"❌ Error saving database: {e}")
            return False


def add_user_to_database(user_id, user_data):
    """Tambahkan user ke database"""
    db = load_database()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if str(user_id) not in db["users"]:
        db["users"][str(user_id)] = {
            "user_id": user_id,
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "username": user_data.get("username", ""),
            "first_seen": current_time,
            "last_seen": current_time,
            "request_count": 1
        }
    else:
        db["users"][str(user_id)]["last_seen"] = current_time
        db["users"][str(user_id)]["first_name"] = user_data.get("first_name", "")
        db["users"][str(user_id)]["last_name"] = user_data.get("last_name", "")
        db["users"][str(user_id)]["username"] = user_data.get("username", "")
        db["users"][str(user_id)]["request_count"] = db["users"][str(user_id)].get("request_count", 0) + 1
    
    save_database(db)


def get_all_users():
    """Ambil semua user dari database"""
    db = load_database()
    return db.get("users", {})


# ==================== HELPER FUNCTIONS ====================

def safe_delete_message(chat_id, message_id):
    """Hapus message dengan aman (tidak error jika gagal)"""
    try:
        bot.delete_message(chat_id, message_id)
        return True
    except Exception as e:
        print(f"⚠️ Failed to delete message: {e}")
        return False


def send_or_edit_message(chat_id, message_id, text, markup=None, parse_mode=None):
    """
    Universal function untuk kirim atau edit message
    Otomatis handle photo vs text message
    """
    try:
        # Coba edit dulu
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup,
            parse_mode=parse_mode
        )
        return True
    except telebot.apihelper.ApiException as e:
        error_msg = str(e).lower()
        if any(err in error_msg for err in [
            "there is no text",
            "message is not modified",
            "message can't be edited",
            "message to edit not found",
            "message to delete not found"
        ]):
            safe_delete_message(chat_id, message_id)
            try:
                bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=markup,
                    parse_mode=parse_mode
                )
                return True
            except Exception as send_error:
                print(f"❌ Error sending message: {send_error}")
                return False
        else:
            print(f"❌ Error editing message: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error in send_or_edit_message: {e}")
        return False


def is_owner(user_id):
    """Cek apakah user adalah owner"""
    return user_id == OWNER_ID


def format_phone_number(phone_number):
    """Format nomor telepon dengan error handling"""
    try:
        parsed = phonenumbers.parse(f"+{phone_number}")
        if phonenumbers.is_valid_number(parsed):
            formatted = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            country_code = phonenumbers.region_code_for_country_code(
                parsed.country_code
            )
            return formatted, country_code
        else:
            return f"+{phone_number}", None
    except Exception as e:
        print(f"⚠️ Error formatting phone: {e}")
        return f"+{phone_number}", None


def get_cached_countries():
    """Ambil list negara dengan caching"""
    global country_cache
    current_time = time.time()
    
    # Cek apakah cache masih valid
    if country_cache["data"] and (current_time - country_cache["timestamp"]) < CACHE_DURATION:
        return country_cache["data"]
    
    # Ambil data baru
    try:
        engine = VNEngine()
        negara_list = engine.ambil_negara_online()
        
        if negara_list:
            country_cache["data"] = negara_list
            country_cache["timestamp"] = current_time
            return negara_list
    except Exception as e:
        print(f"❌ Error getting countries: {e}")
    
    # Return cache lama jika ada error
    return country_cache["data"] if country_cache["data"] else []


# ==================== INISIALISASI BOT ====================

try:
    bot = telebot.TeleBot(utils.ambil_token())
    bot_info = bot.get_me()
    print("=" * 40)
    print("✅ Bot berhasil dijalankan!")
    print("🆔 ID Bot:", bot_info.id)
    print("👤 Username: @" + str(bot_info.username))
    print("=" * 40)
except Exception as e:
    print(f"❌ Error menjalankan bot: {str(e)}")
    exit(1)


# ==================== COMMAND HANDLERS ====================

@bot.message_handler(commands=["start", "mulai"])
@error_handler
def handler_perintah_start(message):
    """Handler untuk perintah /start"""
    user = User(message.from_user)
    
    # Simpan user ke database
    user_data = {
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or "",
        "username": message.from_user.username or ""
    }
    add_user_to_database(message.from_user.id, user_data)
    
    # Ambil info untuk ditampilkan
    users = get_all_users()
    total_users = len(users)
    current_datetime = datetime.now()
    tanggal = current_datetime.strftime("%d %B %Y")
    jam = current_datetime.strftime("%H:%M:%S")
    username = f"@{message.from_user.username}" if message.from_user.username else "Tidak ada"
    user_id = message.from_user.id
    
    pesan_selamat_datang = (
        f"👋 Halo {user.nama_lengkap}!\n\n"
        f" Selamat datang di Bot Nomor Virtual\n"
        f" Bot ini memberikan nomor virtual gratis\n"
        f" dari berbagai negara yang bisa kamu gunakan\n"
        f"│ untuk verifikasi SMS.\n"
        f"╰────────────\n\n"
        f"╭── INFO AKUN\n"
        f"│ 👤 Username: {username}\n"
        f"│ 🆔 ID: `{user_id}`\n"
        f"│ 📅 Tanggal: {tanggal}\n"
        f"│ 🕒 Jam: {jam}\n"
        f"│\n"
        f"│ 👥 Total User: {total_users}\n"
        f"│ 👨‍💻 Developer: {DEVELOPER}\n"
        f"╰────────────\n\n"
        f"╭── PERINTAH TERSEDIA\n"
        f"│ • /nomor - Dapatkan nomor virtual\n"
        f"│ • /bantuan - Lihat panduan lengkap\n"
        f"│ • /tentang - Info tentang bot\n"
        f"│ • Atau gunakan button di bawah ini\n"
        f"╰────────────\n\n"
        f"Silakan pilih menu di bawah:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_nomor = types.InlineKeyboardButton(
        text="📞 Dapatkan Nomor",
        callback_data="get_nomor"
    )
    btn_bantuan = types.InlineKeyboardButton(
        text="📜 Bantuan",
        callback_data="bantuan"
    )
    btn_tentang = types.InlineKeyboardButton(
        text="ℹ️ Tentang",
        callback_data="tentang"
    )
    btn_developer = types.InlineKeyboardButton(
        text="💬 Developer",
        url="https://t.me/Jeeyhosting"
    )
    markup.row(btn_nomor, btn_bantuan)
    markup.row(btn_tentang, btn_developer)
    
    bot.send_chat_action(message.chat.id, "typing")
    bot.reply_to(message, pesan_selamat_datang, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(commands=["help", "bantuan"])
@error_handler
def handler_perintah_bantuan(message):
    """Handler untuk perintah /bantuan"""
    pesan_bantuan = (
   "<b>📖 Panduan Penggunaan Bot</b>\n\n"

"<b>🔹 Cara Mengambil Nomor Virtual</b>\n"
"Gunakan perintah /nomor atau tekan tombol 'Dapatkan Nomor'. Bot akan mencari nomor aktif dari negara yang tersedia dan menampilkan informasi lengkapnya.\n\n"

"<b>🔹 Fitur Setelah Mendapat Nomor</b>\n"
"• <b>Inbox</b> - Lihat SMS yang masuk\n"
"• <b>Ganti Nomor</b> - Ambil nomor baru\n"
"• <b>Cek Profil Telegram</b> - Verifikasi akun Telegram\n"
"• <b>Menu Utama</b> - Kembali ke halaman awal\n"
"• Support semua sosial media\n\n"

"<b>🔹 Tentang Inbox SMS</b>\n"
"Pesan muncul otomatis saat tersedia. Gunakan tombol navigasi untuk melihat pesan lainnya dan tombol Refresh untuk memperbarui.\n\n"

"<b>🔹 Hal Penting yang Perlu Diketahui</b>\n"
"• Nomor bersifat publik dan sementara\n"
"• Jangan gunakan untuk data sensitif\n"
"• Ketersediaan negara tergantung layanan\n\n"

"<b>🔹 Tips Penggunaan</b>\n"
"• Tunggu beberapa menit sebelum refresh\n"
"• Ganti nomor jika tidak menerima kode\n"
"• Coba negara lain jika diperlukan\n"
"• Hindari mengirim OTP berulang kali\n\n"

"<b>🔹 Jika Nomor Tidak Berfungsi</b>\n"
"Ambil nomor baru, coba negara lain, atau tunggu beberapa saat.\n\n"

"<b>🔹 Fitur Pengingat Sholat</b>\n"
"Bot mengirim pengingat otomatis untuk waktu Subuh, Dzuhur, Ashar, Maghrib, dan Isya setiap hari.\n\n"

"💬 Butuh bantuan? Hubungi developer melalui tombol di bawah."
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_menu = types.InlineKeyboardButton(
        text="🔙 Menu Utama",
        callback_data="menu_utama"
    )
    btn_developer = types.InlineKeyboardButton(
        text="💬 Developer",
        url="https://t.me/Jeeyhosting"
    )
    markup.add(btn_menu, btn_developer)
    
    bot.send_chat_action(message.chat.id, "typing")
    bot.reply_to(message, pesan_bantuan, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=["about", "tentang"])
@error_handler
def handler_perintah_tentang(message):
    """Handler untuk perintah /tentang"""
    pesan_tentang = (
"<b>ℹ️ Tentang Bot Ini</b>\n\n"

"Bot ini menyediakan nomor virtual dari berbagai negara untuk menerima SMS verifikasi secara otomatis. Dirancang agar mudah digunakan dan stabil untuk kebutuhan testing dan percobaan layanan.\n\n"

"<b>📱 Informasi Bot</b>\n"
"• Nama: Bot Nomor Virtual\n"
"• Versi: 2.8 (Enhanced)\n"
"• Bahasa: Python 3.11\n"
"• Library: pyTelegramBotAPI\n"
"• Developer: By Jeeyhosting\n\n"

"<b>✨ Fitur Utama</b>\n"
"• Nomor virtual dari berbagai negara\n"
"• Pengecekan inbox SMS real-time\n"
"• Filter nomor aktif otomatis\n"
"• Navigasi pesan (pagination)\n"
"• Antarmuka sederhana dengan tombol inline\n"
"• Gratis tanpa biaya\n"
"• Statistik penggunaan dasar\n"
"• Pengingat waktu sholat otomatis\n\n"

"<b>🔒 Privasi</b>\n"
"• Tidak menyimpan data pribadi sensitif\n"
"• Nomor virtual bersifat publik\n"
"• SMS langsung dari penyedia, tidak disimpan bot\n\n"

"<b>⚠️ Disclaimer</b>\n"
"Bot ini untuk keperluan testing, percobaan, dan edukasi. Penggunaan harus mengikuti aturan layanan terkait dan tidak untuk aktivitas ilegal.\n\n"

"👨‍💻 Dibuat oleh @Jeeyhosting"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_menu = types.InlineKeyboardButton(
        text="🔙 Menu Utama",
        callback_data="menu_utama"
    )
    btn_developer = types.InlineKeyboardButton(
        text="💬 Developer",
        url="https://t.me/Jeeyhosting"
    )
    markup.add(btn_menu, btn_developer)
    
    bot.send_chat_action(message.chat.id, "typing")
    bot.reply_to(message, pesan_tentang, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=["number", "nomor"])
@error_handler
def handler_perintah_nomor(message):
    """Handler untuk perintah /nomor"""
    # Simpan user ke database
    user_data = {
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or "",
        "username": message.from_user.username or ""
    }
    add_user_to_database(message.from_user.id, user_data)
    
    bot.send_chat_action(message.chat.id, "typing")
    pesan_loading = bot.reply_to(
        message,
        "🔍 Sedang mencari nomor virtual untuk kamu...\n\n"
        "⏳ Mengambil daftar negara online..."
    )
    
    try:
        negara_list = get_cached_countries()
        
        if not negara_list:
            markup = types.InlineKeyboardMarkup()
            btn_retry = types.InlineKeyboardButton(
                text="🔄 Coba Lagi",
                callback_data="get_nomor"
            )
            btn_menu = types.InlineKeyboardButton(
                text="🔙 Menu Utama",
                callback_data="menu_utama"
            )
            markup.row(btn_retry, btn_menu)
            
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=pesan_loading.message_id,
                text=(
                    "❌ Maaf, sedang tidak ada negara yang online.\n\n"
                    "🔄 Silakan coba lagi dalam beberapa menit."
                ),
                reply_markup=markup
            )
            return
        
        random.shuffle(negara_list)
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=pesan_loading.message_id,
            text=(
                "🔍 Sedang mencari nomor virtual untuk kamu...\n\n"
                f"✅ Ditemukan {len(negara_list)} negara online\n"
                "⏳ Mencari nomor yang aktif..."
            )
        )
        
        nomor_ditemukan = False
        negara_dicoba = 0
        engine = VNEngine()
        
        for negara in negara_list:
            negara_dicoba += 1
            
            try:
                nomor_list = engine.ambil_nomor_negara(negara['name'])
            except Exception as e:
                print(f"⚠️ Error getting numbers for {negara['name']}: {e}")
                continue
            
            if not nomor_list:
                continue
            
            nama_negara = negara['name'].replace("_", " ").title()
            
            # Update progress setiap 3 negara
            if negara_dicoba % 3 == 0:
                try:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=pesan_loading.message_id,
                        text=(
                            "🔍 Sedang mencari nomor virtual untuk kamu...\n\n"
                            f"✅ Ditemukan {len(negara_list)} negara online\n"
                            f"🔄 Mencoba: {nama_negara}\n"
                            f"📊 Progress: {negara_dicoba}/{len(negara_list)}"
                        )
                    )
                except:
                    pass
            
            for waktu_update, nomor_lengkap in nomor_list:
                try:
                    nomor_format, kode_negara = format_phone_number(nomor_lengkap)
                    bendera = get_flag(kode_negara) if kode_negara else "🏳️"
                    
                    if engine.cek_nomor_valid(negara['name'], nomor_lengkap):
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        btn_inbox = types.InlineKeyboardButton(
                            text="📥 Inbox/Sms",
                            callback_data=f"inbox&{negara['name']}&{nomor_lengkap}"
                        )
                        btn_ganti = types.InlineKeyboardButton(
                            text="🔄 Ganti Nomor",
                            callback_data="ganti_nomor"
                        )
                        btn_profil = types.InlineKeyboardButton(
                            text="👤 Cek Profil Telegram",
                            url=f"tg://resolve?phone={nomor_lengkap}"
                        )
                        btn_menu = types.InlineKeyboardButton(
                            text="🔙 Menu Utama",
                            callback_data="menu_utama"
                        )
                        markup.row(btn_inbox, btn_ganti)
                        markup.row(btn_profil)
                        markup.row(btn_menu)
                        
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=pesan_loading.message_id,
                            text=(
                                f"╭──( INFO NOMOR\n"
                                f"│🌍 Negara: {nama_negara} {bendera}\n"
                                f"│📱 Nomor: `{nomor_format}`\n"
                                f"╰────────────\n"
                                f"💡 Gunakan tombol di bawah untuk:\n"
                                f"• Cek inbox SMS masuk\n"
                                f"• Ganti dengan nomor lain\n"
                                f"• Lihat profil Telegram nomor ini\n"
                                f"• Support All Sosial Media\n\n"
                                f"⚠️ Catatan: Nomor ini publik dan tidak instan!"
                            ),
                            parse_mode="Markdown",
                            reply_markup=markup
                        )
                        
                        nomor_ditemukan = True
                        return
                        
                except Exception as e:
                    print(f"⚠️ Error processing nomor: {str(e)}")
                    continue
            
            # Small delay untuk menghindari rate limit
            time.sleep(0.3)
        
        if not nomor_ditemukan:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_retry = types.InlineKeyboardButton(
                text="🔄 Coba Lagi",
                callback_data="get_nomor"
            )
            btn_menu = types.InlineKeyboardButton(
                text="🔙 Menu Utama",
                callback_data="menu_utama"
            )
            markup.row(btn_retry, btn_menu)
            
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=pesan_loading.message_id,
                text=(
                    f"😕 Maaf, tidak ada nomor aktif yang tersedia saat ini.\n\n"
                    f"📊 Telah mencoba {negara_dicoba} negara\n\n"
                    f"💡 Tips:\n"
                    f"• Coba lagi dalam beberapa menit\n"
                    f"• Layanan Platform mungkin sedang penuh\n"
                    f"• Klik tombol 🔄 Coba Lagi untuk retry"
                ),
                reply_markup=markup
            )
    
    except Exception as e:
        print(f"❌ Fatal error in handler_perintah_nomor: {e}")
        import traceback
        traceback.print_exc()
        
        markup = types.InlineKeyboardMarkup()
        btn_retry = types.InlineKeyboardButton(
            text="🔄 Coba Lagi",
            callback_data="get_nomor"
        )
        btn_menu = types.InlineKeyboardButton(
            text="🔙 Menu Utama",
            callback_data="menu_utama"
        )
        markup.row(btn_retry, btn_menu)
        
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=pesan_loading.message_id,
                text=(
                    f"❌ Terjadi kesalahan sistem.\n\n"
                    f"Silakan coba lagi dengan tombol di bawah."
                ),
                reply_markup=markup
            )
        except:
            bot.reply_to(
                message,
                "❌ Terjadi kesalahan. Silakan coba lagi dengan /nomor",
                reply_markup=markup
            )


# ==================== ADMIN COMMANDS ====================

@bot.message_handler(commands=["admin"])
@owner_only
@error_handler
def handler_admin_panel(message):
    """Handler untuk panel admin (hanya owner)"""
    users = get_all_users()
    total_users = len(users)
    
    pesan_admin = (
        "🔐 ADMIN PANEL\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Users: {total_users}\n"
        f"📁 Database: {DATABASE_FILE}\n\n"
        "Pilih menu admin:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_list_users = types.InlineKeyboardButton(
        text="📋 List Users",
        callback_data="admin_list_users"
    )
    btn_broadcast = types.InlineKeyboardButton(
        text="📢 Broadcast",
        callback_data="admin_broadcast"
    )
    btn_stats = types.InlineKeyboardButton(
        text="📊 Statistics",
        callback_data="admin_stats"
    )
    btn_cache_clear = types.InlineKeyboardButton(
        text="🗑️ Clear Cache",
        callback_data="admin_clear_cache"
    )
    markup.row(btn_list_users, btn_broadcast)
    markup.row(btn_stats, btn_cache_clear)
    
    bot.send_chat_action(message.chat.id, "typing")
    bot.reply_to(message, pesan_admin, reply_markup=markup)


@bot.message_handler(commands=["listusers"])
@owner_only
@error_handler
def handler_list_users(message):
    """Handler untuk melihat daftar semua user (hanya owner)"""
    users = get_all_users()
    
    if not users:
        bot.reply_to(message, "❌ Tidak ada user di database.")
        return
    
    pesan = "📋 DAFTAR SEMUA USER\n━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for idx, (user_id, user_info) in enumerate(users.items(), 1):
        nama = user_info.get("first_name", "Unknown")
        if user_info.get("last_name"):
            nama += f" {user_info.get('last_name')}"
        
        username = user_info.get("username", "No username")
        first_seen = user_info.get("first_seen", "N/A")
        last_seen = user_info.get("last_seen", "N/A")
        request_count = user_info.get("request_count", 0)
        
        pesan += (
            f"{idx}. 👤 {nama}\n"
            f"   🆔 ID: `{user_id}`\n"
            f"   📱 Username: @{username}\n"
            f"   🕐 First: {first_seen}\n"
            f"   🕑 Last: {last_seen}\n"
            f"   📊 Requests: {request_count}\n\n"
        )
        
        # Kirim per 15 user untuk menghindari message terlalu panjang
        if idx % 15 == 0:
            bot.send_message(message.chat.id, pesan, parse_mode="Markdown")
            pesan = ""
            time.sleep(0.5)
    
    if pesan:
        bot.send_message(message.chat.id, pesan, parse_mode="Markdown")


@bot.message_handler(commands=["broadcast"])
@owner_only
@error_handler
def handler_broadcast_command(message):
    """Handler untuk broadcast message ke semua user (hanya owner)"""
    pesan_instruksi = (
        "📢 PESAN SIARAN\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Kirim pesan yang ingin kamu siaran ke semua user.\n\n"
        "Format: /broadcast <pesan>\n\n"
        "Contoh:\n"
        "`/broadcast Halo semua! Bot sedang maintenance hari ini.`\n\n"
        "⚠️ Pesan akan dikirim ke semua user yang terdaftar di database!"
    )
    
    # Cek apakah ada pesan setelah command
    try:
        pesan_broadcast = message.text.split("/broadcast", 1)[1].strip()
        
        if not pesan_broadcast:
            bot.reply_to(message, pesan_instruksi, parse_mode="Markdown")
            return
        
        # Konfirmasi broadcast
        users = get_all_users()
        total_users = len(users)
        
        konfirmasi = (
            f"📢 KONFIRMASI BROADCAST\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 Target: {total_users} users\n\n"
            f"📝 Pesan:\n{pesan_broadcast}\n\n"
            f"Yakin ingin mengirim?"
        )
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_confirm = types.InlineKeyboardButton(
            text="✅ Ya, Kirim",
            callback_data=f"broadcast_confirm"
        )
        btn_cancel = types.InlineKeyboardButton(
            text="❌ Batal",
            callback_data="broadcast_cancel"
        )
        markup.add(btn_confirm, btn_cancel)
        
        # Simpan pesan broadcast sementara (dalam dictionary)
        broadcast_storage[message.from_user.id] = pesan_broadcast
        
        bot.reply_to(message, konfirmasi, reply_markup=markup)
        
    except IndexError:
        bot.reply_to(message, pesan_instruksi, parse_mode="Markdown")


@bot.message_handler(commands=["stats"])
@owner_only
@error_handler
def handler_stats(message):
    """Handler untuk melihat statistik bot (hanya owner)"""
    users = get_all_users()
    total_users = len(users)
    
    # Hitung user baru (hari ini)
    today = datetime.now().strftime("%Y-%m-%d")
    new_users_today = 0
    active_users_today = 0
    total_requests = 0
    
    for user_id, user_info in users.items():
        first_seen = user_info.get("first_seen", "")
        last_seen = user_info.get("last_seen", "")
        request_count = user_info.get("request_count", 0)
        
        if today in first_seen:
            new_users_today += 1
        
        if today in last_seen:
            active_users_today += 1
        
        total_requests += request_count
    
    avg_requests = total_requests / total_users if total_users > 0 else 0
    
    pesan_stats = (
        "📊 STATISTIK BOT\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Users: {total_users}\n"
        f"🆕 User Baru Hari Ini: {new_users_today}\n"
        f"✅ User Aktif Hari Ini: {active_users_today}\n"
        f"📈 Total Requests: {total_requests}\n"
        f"📊 Avg Requests/User: {avg_requests:.2f}\n\n"
        f"📅 Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"💾 Database: {DATABASE_FILE}\n"
        f"🗄️ Cache Status: {'Active' if country_cache['data'] else 'Empty'}"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_refresh = types.InlineKeyboardButton(
        text="🔄 Refresh",
        callback_data="admin_stats"
    )
    markup.add(btn_refresh)
    
    bot.send_chat_action(message.chat.id, "typing")
    bot.reply_to(message, pesan_stats, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
@error_handler
def handler_pesan_default(message):
    """Handler untuk pesan yang tidak dikenali"""
    # Simpan user ke database
    user_data = {
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or "",
        "username": message.from_user.username or ""
    }
    add_user_to_database(message.from_user.id, user_data)
    
    pesan_bantuan_singkat = (
        "🤖 Maaf, saya tidak mengerti pesan itu.\n\n"
        "📱 Perintah yang tersedia:\n"
        "• /nomor - Dapatkan nomor virtual\n"
        "• /bantuan - Lihat panduan\n"
        "• /tentang - Info bot"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_nomor = types.InlineKeyboardButton(
        text="📱 Dapatkan Nomor",
        callback_data="get_nomor"
    )
    btn_menu = types.InlineKeyboardButton(
        text="🔙 Menu Utama",
        callback_data="menu_utama"
    )
    markup.add(btn_nomor, btn_menu)
    
    bot.reply_to(message, pesan_bantuan_singkat, reply_markup=markup)


# ==================== CALLBACK HANDLERS ====================

@bot.callback_query_handler(func=lambda call: call.data == "menu_utama")
@error_handler
def callback_menu_utama(call):
    """Handler untuk tombol Menu Utama"""
    bot.answer_callback_query(call.id)
    
    user = User(call.from_user)
    
    # Ambil info untuk ditampilkan
    users = get_all_users()
    total_users = len(users)
    current_datetime = datetime.now()
    tanggal = current_datetime.strftime("%d %B %Y")
    jam = current_datetime.strftime("%H:%M:%S")
    username = f"@{call.from_user.username}" if call.from_user.username else "Tidak ada"
    user_id = call.from_user.id
    
    pesan_menu = (
        f"👋 Halo {user.nama_lengkap}!\n\n"
        f" Selamat datang di Bot Nomor Virtual\n"
        f" Bot ini memberikan nomor virtual gratis\n"
        f" dari berbagai negara yang bisa kamu gunakan\n"
        f"│ untuk verifikasi SMS.\n"
        f"╰────────────\n\n"
        f"╭── INFO AKUN\n"
        f"│ 👤 Username: {username}\n"
        f"│ 🆔 ID: `{user_id}`\n"
        f"│ 📅 Tanggal: {tanggal}\n"
        f"│ 🕒 Jam: {jam}\n"
        f"│\n"
        f"│ 👥 Total User: {total_users}\n"
        f"│ 👨‍💻 Developer: {DEVELOPER}\n"
        f"╰────────────\n\n"
        f"╭── PERINTAH TERSEDIA\n"
        f"│ • /nomor - Dapatkan nomor virtual\n"
        f"│ • /bantuan - Lihat panduan lengkap\n"
        f"│ • /tentang - Info tentang bot\n"
        f"│ • Atau gunakan button di bawah ini\n"
        f"╰────────────\n\n"
        f"Silakan pilih menu di bawah:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_nomor = types.InlineKeyboardButton(
        text="📞 Dapatkan Nomor",
        callback_data="get_nomor"
    )
    btn_bantuan = types.InlineKeyboardButton(
        text="📜 Bantuan",
        callback_data="bantuan"
    )
    btn_tentang = types.InlineKeyboardButton(
        text="ℹ️ Tentang",
        callback_data="tentang"
    )
    btn_developer = types.InlineKeyboardButton(
        text="💬 Developer",
        url="https://t.me/Jeeyhosting"
    )
    markup.row(btn_nomor, btn_bantuan)
    markup.row(btn_tentang, btn_developer)
    
    send_or_edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=pesan_menu,
        markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data == "get_nomor")
@error_handler
def callback_get_nomor(call):
    """Handler untuk tombol Dapatkan Nomor"""
    bot.answer_callback_query(call.id, "🔍 Mencari nomor...", show_alert=False)
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Simpan user ke database
    user_data = {
        "first_name": call.from_user.first_name or "",
        "last_name": call.from_user.last_name or "",
        "username": call.from_user.username or ""
    }
    add_user_to_database(call.from_user.id, user_data)
    
    send_or_edit_message(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            "🔍 Sedang mencari nomor virtual untuk kamu...\n\n"
            "⏳ Mengambil daftar negara online..."
        )
    )
    
    try:
        negara_list = get_cached_countries()
        
        if not negara_list:
            markup = types.InlineKeyboardMarkup()
            btn_retry = types.InlineKeyboardButton(
                text="🔄 Coba Lagi",
                callback_data="get_nomor"
            )
            btn_menu = types.InlineKeyboardButton(
                text="🔙 Menu Utama",
                callback_data="menu_utama"
            )
            markup.row(btn_retry, btn_menu)
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    "❌ Maaf, sedang tidak ada negara yang online.\n\n"
                    "Silakan coba lagi beberapa saat lagi."
                ),
                reply_markup=markup
            )
            return
        
        random.shuffle(negara_list)
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=(
                "🔍 Sedang mencari nomor virtual untuk kamu...\n\n"
                f"✅ Ditemukan {len(negara_list)} negara online\n"
                "⏳ Mencari nomor yang aktif..."
            )
        )
        
        nomor_ditemukan = False
        negara_dicoba = 0
        engine = VNEngine()
        
        for negara in negara_list:
            negara_dicoba += 1
            
            try:
                nomor_list = engine.ambil_nomor_negara(negara['name'])
            except Exception as e:
                print(f"⚠️ Error getting numbers: {e}")
                continue
            
            if not nomor_list:
                continue
            
            nama_negara = negara['name'].replace("_", " ").title()
            
            for waktu_update, nomor_lengkap in nomor_list:
                try:
                    nomor_format, kode_negara = format_phone_number(nomor_lengkap)
                    bendera = get_flag(kode_negara) if kode_negara else "🏳️"
                    
                    if engine.cek_nomor_valid(negara['name'], nomor_lengkap):
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        btn_inbox = types.InlineKeyboardButton(
                            text="📥 Inbox/Sms",
                            callback_data=f"inbox&{negara['name']}&{nomor_lengkap}"
                        )
                        btn_ganti = types.InlineKeyboardButton(
                            text="🔄 Ganti Nomor",
                            callback_data="ganti_nomor"
                        )
                        btn_profil = types.InlineKeyboardButton(
                            text="👤 Cek Profil Telegram",
                            url=f"tg://resolve?phone={nomor_lengkap}"
                        )
                        btn_menu = types.InlineKeyboardButton(
                            text="🔙 Menu Utama",
                            callback_data="menu_utama"
                        )
                        markup.row(btn_inbox, btn_ganti)
                        markup.row(btn_profil)
                        markup.row(btn_menu)
                        
                        bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=(
                                f"╭──( INFO NOMOR\n"
                                f"│🌍 Negara: {nama_negara} {bendera}\n"
                                f"│📱 Nomor: `{nomor_format}`\n"
                                f"╰────────────\n"
                                f"💡 Gunakan tombol di bawah untuk:\n"
                                f"• Cek inbox SMS masuk\n"
                                f"• Ganti dengan nomor lain\n"
                                f"• Lihat profil Telegram nomor ini\n"
                                f"• Support All Sosial Media\n\n"
                                f"⚠️ Catatan: Nomor ini publik dan tidak instan!"
                            ),
                            parse_mode="Markdown",
                            reply_markup=markup
                        )
                        
                        nomor_ditemukan = True
                        return
                        
                except Exception as e:
                    print(f"⚠️ Error: {e}")
                    continue
            
            time.sleep(0.3)
        
        if not nomor_ditemukan:
            markup = types.InlineKeyboardMarkup()
            btn_retry = types.InlineKeyboardButton(
                text="🔄 Coba Lagi",
                callback_data="get_nomor"
            )
            btn_menu = types.InlineKeyboardButton(
                text="🔙 Menu Utama",
                callback_data="menu_utama"
            )
            markup.row(btn_retry, btn_menu)
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    f"😕 Maaf, tidak ada nomor aktif yang tersedia saat ini.\n\n"
                    f"📊 Telah mencoba {negara_dicoba} negara\n\n"
                    f"💡 Tips:\n"
                    f"• Coba lagi dalam beberapa menit\n"
                    f"• Layanan Platform mungkin sedang penuh"
                ),
                reply_markup=markup
            )
    
    except Exception as e:
        print(f"❌ Error in callback_get_nomor: {e}")
        import traceback
        traceback.print_exc()


@bot.callback_query_handler(func=lambda call: call.data == "bantuan")
@error_handler
def callback_bantuan(call):
    """Handler untuk tombol Bantuan"""
    bot.answer_callback_query(call.id)
    
    pesan_bantuan = (
"<b>📖 Panduan Penggunaan Bot</b>\n\n"

"<b>🔹 Cara Mengambil Nomor Virtual</b>\n"
"Gunakan perintah /nomor atau tekan tombol 'Dapatkan Nomor'. Bot akan mencari nomor aktif dari negara yang tersedia dan menampilkan informasi lengkapnya.\n\n"

"<b>🔹 Fitur Setelah Mendapat Nomor</b>\n"
"• <b>Inbox</b> - Lihat SMS yang masuk\n"
"• <b>Ganti Nomor</b> - Ambil nomor baru\n"
"• <b>Cek Profil Telegram</b> - Verifikasi akun Telegram\n"
"• <b>Menu Utama</b> - Kembali ke halaman awal\n"
"• Support semua sosial media\n\n"

"<b>🔹 Tentang Inbox SMS</b>\n"
"Pesan muncul otomatis saat tersedia. Gunakan tombol navigasi untuk melihat pesan lainnya dan tombol Refresh untuk memperbarui.\n\n"

"<b>🔹 Hal Penting yang Perlu Diketahui</b>\n"
"• Nomor bersifat publik dan sementara\n"
"• Jangan gunakan untuk data sensitif\n"
"• Ketersediaan negara tergantung layanan\n\n"

"<b>🔹 Tips Penggunaan</b>\n"
"• Tunggu beberapa menit sebelum refresh\n"
"• Ganti nomor jika tidak menerima kode\n"
"• Coba negara lain jika diperlukan\n"
"• Hindari mengirim OTP berulang kali\n\n"

"<b>🔹 Jika Nomor Tidak Berfungsi</b>\n"
"Ambil nomor baru, coba negara lain, atau tunggu beberapa saat.\n\n"

"<b>🔹 Fitur Pengingat Sholat</b>\n"
"Bot mengirim pengingat otomatis untuk waktu Subuh, Dzuhur, Ashar, Maghrib, dan Isya setiap hari.\n\n"

"💬 Butuh bantuan? Hubungi developer melalui tombol di bawah."
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_menu = types.InlineKeyboardButton(
        text="🔙 Menu Utama",
        callback_data="menu_utama"
    )
    btn_developer = types.InlineKeyboardButton(
        text="💬 Developer",
        url="https://t.me/Jeeyhosting"
    )
    markup.add(btn_menu, btn_developer)
    
    send_or_edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=pesan_bantuan,
        markup=markup,
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data == "tentang")
@error_handler
def callback_tentang(call):
    """Handler untuk tombol Tentang"""
    bot.answer_callback_query(call.id)
    
    pesan_tentang = (
"<b>ℹ️ Tentang Bot Ini</b>\n\n"

"Bot ini menyediakan nomor virtual dari berbagai negara untuk menerima SMS verifikasi secara otomatis. Dirancang agar mudah digunakan dan stabil untuk kebutuhan testing dan percobaan layanan.\n\n"

"<b>📱 Informasi Bot</b>\n"
"• Nama: Bot Nomor Virtual\n"
"• Versi: 2.8 (Enhanced)\n"
"• Bahasa: Python 3.11\n"
"• Library: pyTelegramBotAPI\n"
"• Developer: By Jeeyhosting\n\n"

"<b>✨ Fitur Utama</b>\n"
"• Nomor virtual dari berbagai negara\n"
"• Pengecekan inbox SMS real-time\n"
"• Filter nomor aktif otomatis\n"
"• Navigasi pesan (pagination)\n"
"• Antarmuka sederhana dengan tombol inline\n"
"• Gratis tanpa biaya\n"
"• Statistik penggunaan dasar\n"
"• Pengingat waktu sholat otomatis\n\n"

"<b>🔒 Privasi</b>\n"
"• Tidak menyimpan data pribadi sensitif\n"
"• Nomor virtual bersifat publik\n"
"• SMS langsung dari penyedia, tidak disimpan bot\n\n"

"<b>⚠️ Disclaimer</b>\n"
"Bot ini untuk keperluan testing, percobaan, dan edukasi. Penggunaan harus mengikuti aturan layanan terkait dan tidak untuk aktivitas ilegal.\n\n"

"👨‍💻 Dibuat oleh @Jeeyhosting"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_menu = types.InlineKeyboardButton(
        text="🔙 Menu Utama",
        callback_data="menu_utama"
    )
    btn_developer = types.InlineKeyboardButton(
        text="💬 Developer",
        url="https://t.me/Jeeyhosting"
    )
    markup.add(btn_menu, btn_developer)
    
    send_or_edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=pesan_tentang,
        markup=markup,
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("inbox"))
@error_handler
def handler_inbox(call):
    """Handler untuk tombol Inbox dengan pagination"""
    parts = call.data.split("&")
    
    if len(parts) == 3:
        _, negara, nomor = parts
        page = 0
    else:
        _, negara, nomor, page = parts
        page = int(page)
    
    try:
        engine = VNEngine()
        pesan_list = engine.ambil_inbox_nomor(negara, nomor)
        
        if not pesan_list:
            bot.answer_callback_query(
                call.id,
                "📭 Inbox kosong atau tidak ada pesan baru.\n\nCoba lagi dalam 1-2 menit!",
                show_alert=True
            )
            return
        
        pesan_list = pesan_list[:10]  # Ambil max 10 pesan
        total_pesan = len(pesan_list)
        
        if page >= total_pesan:
            page = total_pesan - 1
        
        current_pesan = pesan_list[page]
        
        pesan_text = "📬 INBOX SMS\n" + "━" * 30 + "\n\n"
        
        for waktu, isi_pesan in current_pesan.items():
            isi_bersih = isi_pesan.split('received from OnlineSIM.io')[0].strip()
            
            # Potong jika terlalu panjang
            if len(isi_bersih) > 500:
                isi_bersih = isi_bersih[:500] + "..."
            
            pesan_text += (
                f"📨 Pesan #{page + 1} dari {total_pesan}\n\n"
                f"🕐 Waktu: {waktu}\n\n"
                f"💬 Isi Pesan:\n`{isi_bersih}`\n\n"
            )
        
        pesan_text += "━" * 30
        
        markup = types.InlineKeyboardMarkup(row_width=3)
        
        nav_buttons = []
        
        if page > 0:
            btn_prev = types.InlineKeyboardButton(
                text="◀️ Prev",
                callback_data=f"inbox_page&{negara}&{nomor}&{page-1}"
            )
            nav_buttons.append(btn_prev)
        
        btn_page = types.InlineKeyboardButton(
            text=f"• {page + 1}/{total_pesan} •",
            callback_data="noop"
        )
        nav_buttons.append(btn_page)
        
        if page < total_pesan - 1:
            btn_next = types.InlineKeyboardButton(
                text="Next ▶️",
                callback_data=f"inbox_page&{negara}&{nomor}&{page+1}"
            )
            nav_buttons.append(btn_next)
        
        markup.row(*nav_buttons)
        
        btn_refresh = types.InlineKeyboardButton(
            text="🔄 Refresh Inbox",
            callback_data=f"inbox&{negara}&{nomor}"
        )
        
        btn_back = types.InlineKeyboardButton(
            text="🔙 Kembali ke Nomor",
            callback_data=f"back_to_number&{negara}&{nomor}"
        )
        
        markup.row(btn_refresh)
        markup.row(btn_back)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=pesan_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        bot.answer_callback_query(
            call.id,
            f"📬 Menampilkan pesan {page + 1} dari {total_pesan}",
            show_alert=False
        )
    
    except Exception as e:
        print(f"❌ Error in handler_inbox: {e}")
        bot.answer_callback_query(
            call.id,
            f"❌ Error: {str(e)}",
            show_alert=True
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_number"))
@error_handler
def handler_back_to_number(call):
    """Handler untuk kembali ke tampilan nomor"""
    _, negara, nomor = call.data.split("&")
    
    nomor_format, kode_negara = format_phone_number(nomor)
    bendera = get_flag(kode_negara) if kode_negara else "🏳️"
    
    nama_negara = negara.replace("_", " ").title()
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_inbox = types.InlineKeyboardButton(
        text="📥 Inbox/Sms",
        callback_data=f"inbox&{negara}&{nomor}"
    )
    btn_ganti = types.InlineKeyboardButton(
        text="🔄 Ganti Nomor",
        callback_data="ganti_nomor"
    )
    btn_profil = types.InlineKeyboardButton(
        text="👤 Cek Profil Telegram",
        url=f"tg://resolve?phone={nomor}"
    )
    btn_menu = types.InlineKeyboardButton(
        text="🔙 Menu Utama",
        callback_data="menu_utama"
    )
    markup.row(btn_inbox, btn_ganti)
    markup.row(btn_profil)
    markup.row(btn_menu)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f"╭──( INFO NOMOR\n"
            f"│🌍 Negara: {nama_negara} {bendera}\n"
            f"│📱 Nomor: `{nomor_format}`\n"
            f"╰────────────\n"
            f"💡 Gunakan tombol di bawah untuk:\n"
            f"• Cek inbox SMS masuk\n"
            f"• Ganti dengan nomor lain\n"
            f"• Lihat profil Telegram nomor ini\n"
            f"• Support All Sosial Media\n\n"
            f"⚠️ Catatan: Nomor ini publik dan tidak instan!"
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "noop")
def handler_noop(call):
    """Handler untuk tombol yang tidak melakukan apa-apa (page indicator)"""
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "ganti_nomor")
@error_handler
def handler_ganti_nomor(call):
    """Handler untuk tombol Ganti Nomor - redirect ke get_nomor"""
    call.data = "get_nomor"
    callback_get_nomor(call)


# ==================== ADMIN CALLBACK HANDLERS ====================

@bot.callback_query_handler(func=lambda call: call.data == "admin_list_users")
@owner_only
@error_handler
def callback_admin_list_users(call):
    """Handler untuk callback list users"""
    bot.answer_callback_query(call.id, "📋 Loading user list...", show_alert=False)
    
    users = get_all_users()
    
    if not users:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ Tidak ada user di database."
        )
        return
    
    pesan = "📋 DAFTAR USER (10 Terakhir)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    
    user_count = 0
    # Sort by last_seen descending
    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1].get("last_seen", ""),
        reverse=True
    )
    
    for user_id, user_info in sorted_users[:10]:
        user_count += 1
        nama = user_info.get("first_name", "Unknown")
        if user_info.get("last_name"):
            nama += f" {user_info.get('last_name')}"
        
        username = user_info.get("username", "No username")
        last_seen = user_info.get("last_seen", "N/A")
        request_count = user_info.get("request_count", 0)
        
        pesan += (
            f"{user_count}. 👤 {nama}\n"
            f"   🆔 `{user_id}`\n"
            f"   📱 @{username}\n"
            f"   🕑 {last_seen}\n"
            f"   📊 Requests: {request_count}\n\n"
        )
    
    total_users = len(users)
    if total_users > 10:
        pesan += f"\n... dan {total_users - 10} user lainnya.\n"
    
    pesan += f"\n📊 Total: {total_users} users"
    
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text="🔙 Admin Panel",
        callback_data="admin_panel"
    )
    markup.add(btn_back)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=pesan,
        parse_mode="Markdown",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
@owner_only
@error_handler
def callback_admin_broadcast(call):
    """Handler untuk callback broadcast"""
    bot.answer_callback_query(call.id)
    
    users = get_all_users()
    total_users = len(users)
    
    pesan = (
        "📢 BROADCAST MESSAGE\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Users: {total_users}\n\n"
        "Gunakan command:\n"
        "`/broadcast <pesan kamu>`\n\n"
        "Contoh:\n"
        "`/broadcast Halo! Bot maintenance 10 menit.`"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text="🔙 Admin Panel",
        callback_data="admin_panel"
    )
    markup.add(btn_back)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=pesan,
        parse_mode="Markdown",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
@owner_only
@error_handler
def callback_admin_stats(call):
    """Handler untuk callback statistics"""
    bot.answer_callback_query(call.id, "🔄 Refreshing stats...", show_alert=False)
    
    users = get_all_users()
    total_users = len(users)
    
    # Hitung stats
    today = datetime.now().strftime("%Y-%m-%d")
    new_users_today = 0
    active_users_today = 0
    total_requests = 0
    
    for user_id, user_info in users.items():
        first_seen = user_info.get("first_seen", "")
        last_seen = user_info.get("last_seen", "")
        request_count = user_info.get("request_count", 0)
        
        if today in first_seen:
            new_users_today += 1
        
        if today in last_seen:
            active_users_today += 1
        
        total_requests += request_count
    
    avg_requests = total_requests / total_users if total_users > 0 else 0
    
    pesan_stats = (
        "📊 STATISTIK BOT\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Users: {total_users}\n"
        f"🆕 User Baru Hari Ini: {new_users_today}\n"
        f"✅ User Aktif Hari Ini: {active_users_today}\n"
        f"📈 Total Requests: {total_requests}\n"
        f"📊 Avg Requests/User: {avg_requests:.2f}\n\n"
        f"📅 Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"💾 Database: {DATABASE_FILE}\n"
        f"🗄️ Cache: {'Active' if country_cache['data'] else 'Empty'}"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_refresh = types.InlineKeyboardButton(
        text="🔄 Refresh",
        callback_data="admin_stats"
    )
    btn_back = types.InlineKeyboardButton(
        text="🔙 Admin Panel",
        callback_data="admin_panel"
    )
    markup.row(btn_refresh, btn_back)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=pesan_stats,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
@owner_only
@error_handler
def callback_admin_panel(call):
    """Handler untuk kembali ke admin panel"""
    bot.answer_callback_query(call.id)
    
    users = get_all_users()
    total_users = len(users)
    
    pesan_admin = (
        "🔐 ADMIN PANEL\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Users: {total_users}\n"
        f"📁 Database: {DATABASE_FILE}\n\n"
        "Pilih menu admin:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_list_users = types.InlineKeyboardButton(
        text="📋 List Users",
        callback_data="admin_list_users"
    )
    btn_broadcast = types.InlineKeyboardButton(
        text="📢 Broadcast",
        callback_data="admin_broadcast"
    )
    btn_stats = types.InlineKeyboardButton(
        text="📊 Statistics",
        callback_data="admin_stats"
    )
    btn_cache_clear = types.InlineKeyboardButton(
        text="🗑️ Clear Cache",
        callback_data="admin_clear_cache"
    )
    markup.row(btn_list_users, btn_broadcast)
    markup.row(btn_stats, btn_cache_clear)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=pesan_admin,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "admin_clear_cache")
@owner_only
@error_handler
def callback_admin_clear_cache(call):
    """Handler untuk clear cache"""
    global country_cache
    
    country_cache = {"data": None, "timestamp": 0}
    
    bot.answer_callback_query(
        call.id,
        "✅ Cache berhasil dibersihkan!",
        show_alert=True
    )
    
    # Redirect ke admin panel
    call.data = "admin_panel"
    callback_admin_panel(call)


@bot.callback_query_handler(func=lambda call: call.data == "broadcast_confirm")
@owner_only
@error_handler
def callback_broadcast_confirm(call):
    """Handler untuk konfirmasi broadcast"""
    bot.answer_callback_query(call.id, "📤 Mengirim broadcast...", show_alert=False)
    
    pesan_broadcast = broadcast_storage.get(call.from_user.id)
    
    if not pesan_broadcast:
        bot.answer_callback_query(call.id, "❌ Pesan broadcast tidak ditemukan", show_alert=True)
        return
    
    users = get_all_users()
    
    sukses = 0
    gagal = 0
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f"📤 BROADCASTING...\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏳ Mengirim ke {len(users)} users...\n"
            f"Mohon tunggu..."
        )
    )
    
    for user_id in users.keys():
        try:
            bot.send_message(
                chat_id=int(user_id),
                text=f"<pre>{pesan_broadcast}</pre>",
                parse_mode="HTML"
            )
            sukses += 1
            time.sleep(0.05)  # Delay untuk menghindari rate limit
        except Exception as e:
            print(f"⚠️ Failed to send to {user_id}: {e}")
            gagal += 1
    
    hasil = (
        f"✅ BROADCAST SELESAI!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Hasil:\n"
        f"✅ Berhasil: {sukses}\n"
        f"❌ Gagal: {gagal}\n"
        f"📱 Total: {len(users)}\n\n"
        f"⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(
        text="🔙 Admin Panel",
        callback_data="admin_panel"
    )
    markup.add(btn_back)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=hasil,
        reply_markup=markup
    )
    
    # Hapus pesan broadcast dari storage
    if call.from_user.id in broadcast_storage:
        del broadcast_storage[call.from_user.id]


@bot.callback_query_handler(func=lambda call: call.data == "broadcast_cancel")
@owner_only
@error_handler
def callback_broadcast_cancel(call):
    """Handler untuk cancel broadcast"""
    bot.answer_callback_query(call.id, "❌ Broadcast dibatalkan", show_alert=False)
    
    # Hapus pesan broadcast dari storage
    if call.from_user.id in broadcast_storage:
        del broadcast_storage[call.from_user.id]
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ Broadcast dibatalkan."
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("inbox_page"))
@error_handler
def handler_inbox_pagination(call):
    """Handler untuk pagination inbox"""
    _, negara, nomor, page = call.data.split("&")
    page = int(page)
    
    # Redirect ke handler inbox dengan page number
    call.data = f"inbox&{negara}&{nomor}&{page}"
    handler_inbox(call)


# ==================== MAIN EXECUTION ====================

if __name__ == '__main__':
    print("\n🚀 Bot sedang berjalan...")
    print("💡 Tekan Ctrl+C untuk menghentikan\n")
    
    # Buat database file jika belum ada
    if not os.path.exists(DATABASE_FILE):
        save_database({"users": {}})
        print(f"✅ Database file '{DATABASE_FILE}' telah dibuat\n")
    
    # Start prayer times scheduler in background thread
    try:
        prayer_thread = threading.Thread(target=prayer_times_scheduler, daemon=True)
        prayer_thread.start()
        print("🕌 Prayer times notification scheduler started\n")
    except Exception as e:
        print(f"⚠️ Failed to start prayer times scheduler: {e}\n")
    
    try:
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("\n\n⛔ Bot dihentikan oleh owner")
        prayer_notification_active = False
        print("🕌 Prayer notification scheduler stopped")
        print("👋 Terima kasih telah menggunakan bot ini!\n")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}\n")
        import traceback
        traceback.print_exc()