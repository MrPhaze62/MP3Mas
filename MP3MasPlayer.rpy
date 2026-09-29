# auto submod update

# -- you can tell BonkAMon was here...

# Register the submod
init -990 python:
    store.mas_submod_utils.Submod(
        author="Phazeee",
        name="MP3MasPlayer",
        description="Mp3 Styled MAS Player! Listen to music with her you absolute gamer.",
        version="0.0.7b",
    )


init 10001 python:
    # Dynamically decide the MP3 button based on submods installed in extra menu.
    def get_mp3_button_area():
        ow = store.mas_submod_utils.isSubmodInstalled("Open World")
        bonk = store.mas_submod_utils.isSubmodInstalled("BonkAMon")

        # Adjust MP3 position depending on which submods are present
        if ow and bonk:
            return (530, 639, 202, 65)  # Both installed - button to the right
        elif ow:
            return (310, 639, 202, 65)  # Only Open World - below it.
        elif bonk:
            return (520, 639, 202, 65)  # Only BonkAMon - same spot as before
        else:
            return (310, 639, 202, 65)  # Neither 


init 10001:
    screen mas_extramenu_area():
        zorder 52
        key "e" action Jump("mas_extra_menu_close")
        key "E" action Jump("mas_extra_menu_close")

        frame:
            area(0, 0, 1280, 720)
            background Solid("#0000007F")
            textbutton _("Close"):
                    area (60, 596, 120, 35)
                    style "hkb_button"
                    action Jump("mas_extra_menu_close")
                # zoom control
        frame:
            area (195, 450, 80, 255)
            style "mas_extra_menu_frame"
            vbox:
                spacing 2
                label "Zoom":
                    text_style "mas_extra_menu_label_text"
                    xalign 0.5
                textbutton _("Reset"):
                        style "mas_adjustable_button"
                        selected False
                        xsize 72
                        ysize 35
                        xalign 0.3
                        action SetField(store.mas_sprites, "zoom_level", store.mas_sprites.default_zoom_level)
                bar value FieldValue(store.mas_sprites, "zoom_level", store.mas_sprites.max_zoom):
                    style "mas_adjust_vbar"
                    xalign 0.5
                $ store.mas_sprites.adjust_zoom()

        # OpenWorld Button is here. saw a bug with my button being duplicated twice only here.
        if store.mas_submod_utils.isSubmodInstalled("Open World"):
            frame:
                area (310, 550, 202, 65)
                style "mas_extra_menu_frame"
                if persistent._mas_in_idle_mode:
                    textbutton ("Open World"):
                        xalign 0.5
                        yalign 0.5
                        action NullAction()
                else:
                    textbutton ("Open World"):
                        xalign 0.5
                        yalign 0.5
                        action [Hide("mas_extramenu_area"), Jump("view_OW")] hover_sound gui.hover_sound

        # Surprisingly, BonkAMon had no duplicate buttons with mp3 button, so i done goof somehow but hey, a rewrite.
        if store.mas_submod_utils.isSubmodInstalled("BonkAMon"):
            frame:
                area (310, 639, 202, 65)
                style "mas_extra_menu_frame"
                if persistent._mas_in_idle_mode:
                    textbutton ("Bonk Monika"):
                        xalign 0.5
                        yalign 0.5
                        action NullAction()
                else:
                    textbutton ("Bonk Monika"):
                        xalign 0.5
                        yalign 0.5
                        action [Hide("mas_extramenu_area"), Jump("view_bonkmenu")] hover_sound gui.hover_sound

        # MP3 Player button
        $ mp3_area = get_mp3_button_area()
        frame:
            area mp3_area
            style "mas_extra_menu_frame"
            if persistent._mas_in_idle_mode:
                textbutton ("MP3 Player!"):
                    xalign 0.5
                    yalign 0.5
                    action NullAction()
            else:
                textbutton ("MP3 Player!"):
                    xalign 0.5
                    yalign 0.5
                    action [Hide("mas_extramenu_area"), Jump("MP3PlayerMenu")] hover_sound gui.hover_sound

screen mp3Player_menu():
    zorder 50
    style_prefix "hkb"
    hbox:
        grid 2 1:
            spacing 20
            xpos 527
            ypos 534
            textbutton ("MP3 Player!"): 
                xysize(120, None) 
                action Jump("MP3PlayerMenu") hover_sound gui.hover_sound
            textbutton ("Return") action Jump("mas_extra_menu_close") hover_sound gui.hover_sound
    vbox: 
        xpos 1166
        ypos 0
        textbutton ("Nyeheheheh") action Jump("DevBaka2") hover_sound gui.hover_sound


#ImagesCuzWeBall.

# image bg Test = "Submods/MP3Mas/Mp3Background/test.png" - WIP, was gonna use this for an UI idea... but no clue how to design. ;-;


# Below is the Player Logic. Seriously. mas crashed cuz this is volitile.

define MUSIC_FOLDER = "submods/MP3Mas/music/"
define LYRICS_FOLDER = "submods/MP3Mas/lyrics/"

# Persistent variables
default music_track_list = []
default music_current_index = 0
default music_is_playing = False
# below is the progress bar, we're gonna make it simulated/fake. for UI purposes. not bothered of actually displaying true timing just yet. that's a future me issue.
default music_progress = 0.0        # current progress (0.0–1.0)
default music_progress_time = 0.0   # elapsed seconds
default music_total_time = 180.0    # estimated fake length in seconds (fake default)
# Setting stuff for customisation for the users? funsies.
default persistent.mp3_bg_color = "#ce0f85d2"  # Default pinkish background
default persistent.mp3_accent_color = "#00cc99" 
default persistent.mp3_lcdtrip_color ="#d6ec97"
default persistent.mp3_leftbar_color = "#00cc99"
default persistent.mp3_rightbar_color = "#333333"
# GamerRGB mode heheh. 
default persistent.mp3_rainbow_mode = False
default persistent.mp3_rainbow_index = 0
# Theme: "custom" = the color-picker skin below, "mas" = matches MAS's own UI chrome (hkb_button/mas_extra_menu_frame styles).
default persistent.mp3_theme = "custom"
# Only relevant when mp3_theme == "mas": whether the panel gets a dark backing or stays fully transparent (just the border).
default persistent.mp3_mas_bg_dark = False

# --- Lyrics (LRC) state ---
# current_lyrics is a sorted list of (timestamp_seconds, line_text) tuples
# loaded from LYRICS_FOLDER, matched by filename to the track that's playing.
default current_lyrics = []
default current_lyric_text = ""




init python:
    import os
    import time
    import re
    import io  # io.open() supports encoding = on both Python 2 and 3 - old Ren'Py (7.x) runs Python 2.

    SUPPORTED_AUDIO_EXTS = [".mp3", ".ogg", ".wav", ".flac", ".opus"]
# progress bar simulation. 
    def music_reset_progress():
        global music_progress, music_progress_time
        music_progress = 0.0
        music_progress_time = 0.0

    def music_update_progress(dt=1.0):
        global music_progress, music_progress_time, music_total_time

        # Only move the bar if a song is actually playing.
        if music_is_playing and renpy.music.is_playing(channel="music"):
            music_progress_time += dt
            if music_total_time > 0:
                music_progress = min(1.0, music_progress_time / music_total_time)

        # Piggyback the lyric-line lookup on the same tick, no extra timer needed.
        get_current_lyric_line()

        renpy.restart_interaction()

    #init python:
    def format_time(seconds):
    # Formats seconds into mins/sec. e.g M:SS as in 1:05.
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return "%d:%02d" % (minutes, secs)

    def get_progress_text():
        # Returns the numbers like 0:34 / 3:00
        return "%s / %s" % (format_time(music_progress_time), format_time(music_total_time))
    
    # Volume Slider
    def music_set_volume(vol):
        renpy.music.set_volume(vol, channel="music")
        persistent.mp3_volume = vol
        renpy.save_persistent()
    
    style.mp3_vol_bar = Style(style.bar)
    style.mp3_vol_bar.thumb = Frame(Solid("#ffffff"), 0, 0)
    style.mp3_vol_bar.thumb_offset = 8

    # Rainbow RGB colours for GamerRGB. Now Booplicate approved!
    rainbow_colors = [
        "#ff0000aa", "#ff4400aa", "#ff8800aa", "#ffcc00aa", "#ffff00aa",
        "#88ff00aa", "#00ff00aa", "#00ff88aa", "#00ffffaa", "#0088ffaa",
        "#0000ffaa", "#8800ffaa", "#ff00ffaa", "#ff0088aa"
    ]

    def rainbow_cycle():
        global rainbow_colors
        if persistent.mp3_rainbow_mode:
            persistent.mp3_rainbow_index = (persistent.mp3_rainbow_index + 1) % len(rainbow_colors)
            persistent.mp3_bg_color = rainbow_colors[persistent.mp3_rainbow_index]
            persistent.mp3_accent_color = rainbow_colors[(persistent.mp3_rainbow_index + 4) % len(rainbow_colors)]
            persistent.mp3_lcdtrip_color = rainbow_colors[(persistent.mp3_rainbow_index + 8) % len(rainbow_colors)]
        renpy.restart_interaction()

    # Theme toggle - swaps between the custom color-picker skin and MAS's own UI chrome.
    def toggle_mp3_theme():
        if persistent.mp3_theme == "mas":
            persistent.mp3_theme = "custom"
        else:
            persistent.mp3_theme = "mas"
        renpy.save_persistent()
        renpy.restart_interaction()


    # - LRC (lyric) handling

    # Basic and "enhanced" LRC tag matcher: [mm:ss.xx] or [mm:ss] / source taken from multiple renpy documentation and research.
    LRC_TAG_RE = re.compile(r'\[(\d+):(\d+(?:\.\d+)?)\]')

    def parse_lrc(path):
        # Parses a .lrc file into a sorted list of (seconds, texts).
        lyrics = []
        try:
            with io.open(path, "r", encoding="utf-8", errors="ignore") as f:
                for raw_line in f:
                    tags = LRC_TAG_RE.findall(raw_line)
                    if not tags:
                        continue  # metadata lines like [ar:], [ti:], or plain text - skip
                    text = LRC_TAG_RE.sub("", raw_line).strip()
                    for (mm, ss) in tags:
                        t = int(mm) * 60 + float(ss)
                        lyrics.append((t, text))
        except Exception as e:
            store.mas_utils.mas_log.info("[MP3MasPlayer] Failed to parse LRC '{}': {}".format(path, e))
            return []

        lyrics.sort(key=lambda pair: pair[0])
        return lyrics

    def music_load_lrc(track_filename):
        # Looks for a matching file: "song.mp3" -> "song.lrc" in LYRICS_FOLDER
        # (which is a separate folder from the audio files themselves, makes it easier).
        global current_lyrics, current_lyric_text
        current_lyrics = []
        current_lyric_text = ""

        base, _ext = os.path.splitext(track_filename)
        lrc_relpath = LYRICS_FOLDER + base + ".lrc"

        # Alternative local lyric file searching during multiple testing, it wouldn't find the friggin files, hit and a miss occasionally. now stable though.
        lrc_path = None
        try:
            # Resolves through Ren'Py's archive/search-path system if the
            # lyrics folder ever gets packed into an rpa.
            lrc_path = renpy.loader.transfn(lrc_relpath)
        except Exception:
            lrc_path = None

        if not lrc_path or not os.path.exists(lrc_path):
            # This is the fallback, which checks the raw game directory directly.
            fallback = os.path.join(config.basedir, "game", lrc_relpath)
            if os.path.exists(fallback):
                lrc_path = fallback
            else:
                lrc_path = None

        if lrc_path:
            current_lyrics = parse_lrc(lrc_path)
            if current_lyrics:
                store.mas_utils.mas_log.info("[MP3MasPlayer] Loaded {} lyric lines for {}".format(len(current_lyrics), track_filename))

    def get_current_lyric_line():
        # grabs the most recent lyric line for the current 'real' (simulated) playback position.
        global current_lyric_text

        if not current_lyrics:
            current_lyric_text = ""
            return current_lyric_text

        pos = renpy.music.get_pos(channel="music")
        if pos is None:
            return current_lyric_text

        line = ""
        for (t, text) in current_lyrics:
            if t <= pos:
                line = text
            else:
                break

        current_lyric_text = line
        return current_lyric_text



# Loads all supported audio files from the folder.
    def music_load_tracks():
        
        global music_track_list
        # Rewrite of the music folder check, basically check if folder exists, otherwise, make one for the user?
        try:
            path = renpy.loader.transfn(MUSIC_FOLDER)
        except Exception:
            # If Ren'Py can't resolve it (if folder doesn't exist then we're all doomed.)
            
            full_path = os.path.join(config.basedir, "game", "submods", "MP3Mas", "music")
            if not os.path.exists(full_path):
                try:
                    os.makedirs(full_path)
                    store.mas_utils.mas_log.info("[MP3MasPlayer] Created missing music folder at: {}".format(full_path))
                except Exception as e:
                    store.mas_utils.mas_log.info("[MP3MasPlayer] Failed to create music folder: {}".format(e))
            music_track_list = []
            return music_track_list

        
        if os.path.isdir(path):
            music_track_list = [
                f for f in os.listdir(path)
                if any(f.lower().endswith(ext) for ext in SUPPORTED_AUDIO_EXTS)
            ]
            music_track_list.sort()
        else:
            music_track_list = []

        # We now make sure the lyrics folder exists, same treatment as the music folder above, else we're still doomed.
        try:
            lyrics_path = renpy.loader.transfn(LYRICS_FOLDER)
        except Exception:
            lyrics_path = None

        lyrics_full_path = os.path.join(config.basedir, "game", "submods", "MP3Mas", "lyrics")
        if not lyrics_path and not os.path.exists(lyrics_full_path):
            try:
                os.makedirs(lyrics_full_path)
                store.mas_utils.mas_log.info("[MP3MasPlayer] Created missing lyrics folder at: {}".format(lyrics_full_path))
            except Exception as e:
                store.mas_utils.mas_log.info("[MP3MasPlayer] Failed to create lyrics folder: {}".format(e))

        return music_track_list

    def music_play(index=None):
    # Play a track by index, or resume current song that is playing. DID YOU KNOW RENPY HAS WEIRD AUDIO DOCUMENTATION??
        global music_current_index, music_is_playing
        if not music_track_list:
            music_load_tracks()
            #music_reset_progress()
        if index is not None:
            music_current_index = index
        if not music_track_list:
            return
        #music_reset_progress()
    
    # Check if the music is paused
        if renpy.music.is_playing(channel="music") and not music_is_playing:
            renpy.music.set_pause(False, channel="music")
        else:
            file = MUSIC_FOLDER + music_track_list[music_current_index]
            renpy.music.play(file, channel="music", loop=False)
            music_load_lrc(music_track_list[music_current_index])
    
        music_is_playing = True

    def music_stop():
        renpy.music.stop(channel="music")
        global music_is_playing
        music_is_playing = False
        music_reset_progress()

    def music_pause():
        #Pause or resume the current track, this tripped me off. alot. see? you'd expect it to be simple but no... music never is.
        global music_is_playing

        if renpy.music.is_playing(channel="music"):
            renpy.music.set_pause(True, channel="music")
            music_is_playing = False
        else:
            renpy.music.set_pause(False, channel="music")
            music_is_playing = True


    def music_next():
        global music_current_index
        if not music_track_list:
            return
        music_current_index = (music_current_index + 1) % len(music_track_list)
        music_play(music_current_index)
        music_reset_progress()

    def music_prev():
        global music_current_index
        if not music_track_list:
            return
        music_current_index = (music_current_index - 1) % len(music_track_list)
        music_play(music_current_index)
        music_reset_progress()

# THE ACTUAL UI BELOW! Fear my terrible design for i have no [BLEEP]ing clue how to design for the life of me!

screen mp3_player_screen():
    tag menu
    modal True
    zorder 100

    $ is_mas_theme = (persistent.mp3_theme == "mas")

    if is_mas_theme:
        # ================= MAS-styled skin =================
        # Reuses the same "hkb_button" / "mas_extra_menu_frame" styles the
        # game's own extra-menu buttons use, so this matches MAS's UI chrome
        # instead of approximating it with hardcoded colors.
        frame:
            style "mas_extra_menu_frame"
            if persistent.mp3_mas_bg_dark:
                background Solid("#00000099")
            xalign 0.5
            yalign 0.5
            xsize 700
            ysize 400
            xpadding 20
            ypadding 20

            vbox:
                spacing 12
                xalign 0.5
                yalign 0.5
                style_prefix "hkb"

                text "Monika's MP3 Player" size 26 xalign 0.5

                if music_track_list and 0 <= music_current_index < len(music_track_list):
                    $ current_track = music_track_list[music_current_index]

                    $ status_text = "Stopped"
                    if renpy.music.is_playing(channel="music"):
                        if music_is_playing:
                            $ status_text = "Now Playing:"
                        else:
                            $ status_text = "Paused Song:"
                    else:
                        $ status_text = "Stopped Song:"

                    text status_text size 20 xalign 0.5
                    text current_track size 16 xalign 0.5

                    if current_lyric_text:
                        text current_lyric_text size 16 xalign 0.5

                    bar:
                        value music_progress
                        xsize 400
                        ysize 10
                        xalign 0.5
                    text get_progress_text() size 16 xalign 0.5

                    hbox:
                        spacing 6
                        xalign 0.5

                        textbutton "Prev" text_size 20 action Function(music_prev)
                        textbutton "Play" text_size 20 action Function(music_play)
                        textbutton "Pause" text_size 20 action Function(music_pause)
                        textbutton "Stop" text_size 20 action Function(music_stop)
                        textbutton "Next" text_size 20 action Function(music_next)

                else:
                    text "No tracks found in your MP3 folder! Please make sure there are songs in your game/submods/MP3Mas/music folder" size 16 xalign 0.5

                null height 6

                textbutton "Close":
                    text_size 20
                    xalign 0.5
                    action [Hide("mp3_player_screen"), Jump("MP3Retrun")]

            textbutton "?":
                style "hkb_button"
                text_size 28
                xpos 1.0
                xanchor 1.0
                ypos 0.0
                yanchor 0.0
                xoffset -10
                yoffset 10
                action Show("mp3_info_popup")

            textbutton "Settings":
                style "hkb_button"
                text_size 23
                xpos 1.0
                xanchor 1.0
                ypos 0.0
                yanchor 0.0
                xoffset -10
                yoffset 305
                action Show("mp3_settings_popup")

    else:
        # ================= Custom color-picker skin =================
        frame:
            background Solid(persistent.mp3_bg_color)
            xalign 0.5
            yalign 0.5
            xsize 560
            ysize 380
            xpadding 25
            ypadding 25

            vbox:
                spacing 15
                xalign 0.5
                yalign 0.5

                text "Monika's MP3 Player" color "#66ffcc" size 26 xalign 0.5

                if music_track_list and 0 <= music_current_index < len(music_track_list):
                    $ current_track = music_track_list[music_current_index]

                    # Determine status and colour. Makes it easier to tell whats being played and paused during playback.
                    $ status_text = "Stopped"
                    $ status_color = "#ff8080"

                    # renpy.music.is_playing() returns True if channel has audio (playing or paused) - thanks renpy, i've to remind myself here multiple times. for audio equals nightmare.
                    if renpy.music.is_playing(channel="music"):
                        if music_is_playing:
                            $ status_text = "Now Playing:"
                            $ status_color = "#00cc99"
                        else:
                            $ status_text = "Paused Song:"
                            $ status_color = "#ffcc00"
                    else:
                        $ status_text = "Stopped Song:"
                        $ status_color = "#ff8080"

                    # Show status label
                    text status_text color status_color size 20 xalign 0.5

                    # === LCD-like strip: frame holds the background + padding ===
                    frame:
                        background Solid(persistent.mp3_lcdtrip_color)
                        xalign 0.5
                        xpadding 10
                        ypadding 6
                        # Playback lines here.
                        $ display_line = status_text + " " + current_track #if status_text != "Stopped" else "Song is stopped!"
                        text display_line color "#ffffff" size 18 xalign 0.5

                    # Lyric line, synced against 'real' playback position (this only shows if a matching .lrc file was found in the lyrics folder).
                    if current_lyric_text:
                        frame:
                            background Solid("#00000066")
                            xalign 0.5
                            xpadding 10
                            ypadding 4
                            text current_lyric_text color persistent.mp3_lcdtrip_color size 16 xalign 0.5 # For now, this color is tied to the LCD COLOR STRIP till i get customisation for it.

                    # a simulated progress bar UI is here, now fake in 720p quality! 
                    bar:
                        value music_progress
                        xsize 400
                        ysize 10
                        xalign 0.5
                        left_bar Frame(Solid(persistent.mp3_accent_color), 0, 0)
                        right_bar Frame(Solid("#333333"), 0, 0)
                        thumb None
                    text get_progress_text() color "#ffffff" size 16 xalign 0.5

                    hbox:
                        spacing 12
                        xalign 0.5

                        textbutton "Prev":
                            text_color "#ffffff"
                            background Solid("#333333")
                            hover_background Solid("#00cc99")
                            action Function(music_prev)

                        textbutton "Play":
                            text_color "#ffffff"
                            background Solid("#333333")
                            hover_background Solid("#00cc99")
                            action Function(music_play)

                        textbutton "Pause":
                            text_color "#ffffff"
                            background Solid("#333333")
                            hover_background Solid("#00cc99")
                            action Function(music_pause)

                        textbutton "Stop":
                            text_color "#ffffff"
                            background Solid("#333333")
                            hover_background Solid("#00cc99")
                            action Function(music_stop)

                        textbutton "Next":
                            text_color "#ffffff"
                            background Solid("#333333")
                            hover_background Solid("#00cc99")
                            action Function(music_next)

                else:
                    text "No tracks found in your MP3 folder! Please make sure there are songs in your game/submods/MP3Mas/music folder" color "#ff8080" size 16 xalign 0.5

                null height 10

                textbutton "Close":
                    text_color "#ffffff"
                    background Solid("#333333")
                    hover_background Solid("#df1212")
                    xalign 0.5
                    action [Hide("mp3_player_screen"), Jump("MP3Retrun")]

            # Info button in top right corner... not the left. where the button shot right off the screen beyond the stratosphere... the trauma.
            textbutton "?":
                text_size 28
                text_color "#ffffff"
                background Solid("#333333aa")
                hover_background Solid("#00cc99")
                xpos 1.0
                xanchor 1.0
                ypos 0.0
                yanchor 0.0
                xoffset -10
                yoffset 10
                action Show("mp3_info_popup")


            # Settings button (next to ?)
            textbutton "Settings":
                text_size 23
                text_color "#ffffff"
                background Solid("#333333aa")
                hover_background Solid("#00cc99")
                xpos 1.0
                xanchor 1.0
                ypos 0.0
                yanchor 0.0
                xoffset -10  # slightly left of the ? button
                yoffset 305
                action Show("mp3_settings_popup")

    if persistent.mp3_rainbow_mode and not is_mas_theme:
        timer 0.15 action Function(rainbow_cycle) repeat True

    timer 1.0 action Function(music_update_progress, 1.0) repeat True


#labels land

label ViewMP3Menu2:
    python:
        music_load_tracks()
        if persistent.mp3_volume is None:
            persistent.mp3_volume = 0.8
        music_set_volume(persistent.mp3_volume)
        mas_RaiseShield_dlg()
    call screen mp3_player_screen
    return



label MP3PlayerMenu:
    if not persistent.mp3_player_seen:
        $ persistent.mp3_player_seen = True
        m "I see you've made me an MP3 Music player? Thanks [player]!"
        $ renpy.save_persistent()
    else:
        m "Back to listening to music together, [player]?"
    
    jump ViewMP3Menu2
    return




screen mp3_info_popup():
    modal True
    zorder 200

    frame:
        background Solid("#111111dd")
        xalign 0.5
        yalign 0.5
        xsize 460
        ysize 420
        xpadding 20
        ypadding 20
        vbox:
            spacing 12
            text "MP3Mas Player Help" color "#66ffcc" size 26 xalign 0.5
            text "• Place your music files in: game/submods/MP3Mas/music/" color "#ffffff" size 18
            text "• Supports: MP3, OGG, WAV, FLAC, OPUS" color "#ffffff" size 18
            text "• Use the Play, Pause, Stop, Next, and Prev buttons to control playback." color "#ffffff" size 18
            text "• Monika will remember your last played song!" color "#ffffff" size 18
            text "• The Progress Bar is Simulated/fake. it will always end at 3:00, perhaps a future update may make it real." color "#ffffff" size 18
            text "• Add a matching .lrc file (same name as the song) in game/submods/MP3Mas/lyrics/ for synced lyrics!" color "#ffffff" size 18
            text "• Switch between the custom skin and MAS's own UI look from Settings > Theme." color "#ffffff" size 18

            textbutton "Close":
                text_color "#ffffff"
                background Solid("#333333")
                hover_background Solid("#df1212")
                xalign 0.5
                action Hide("mp3_info_popup")


screen mp3_settings_popup():
    modal True
    zorder 200

    frame:
        background Solid("#111111dd")
        xalign 0.5
        yalign 0.5
        xsize 560
        ysize 560
        xpadding 25
        ypadding 20

        vbox:
            spacing 10
            xalign 0.5

            text "MP3 Player Settings" color "#66ffcc" size 26 xalign 0.5

            # Divider
            frame:
                background Solid("#ffffff22")
                xsize 510
                ysize 2
                xalign 0.5

            # Theme toggle
            vbox:
                spacing 6
                xalign 0.5
                $ theme_label = "Theme: MAS UI" if persistent.mp3_theme == "mas" else "Theme: Custom Skin"
                $ theme_bg = Solid("#3e6ea3") if persistent.mp3_theme == "mas" else Solid("#333333")
                text "Theme:" color "#aaaaaa" size 16 xalign 0.5
                textbutton theme_label:
                    text_color "#ffffff"
                    background theme_bg
                    hover_background Solid("#5588cc")
                    xalign 0.5
                    action Function(toggle_mp3_theme)
                text "(Colors below only apply to the Custom Skin theme)" color "#666666" size 12 xalign 0.5

                if persistent.mp3_theme == "mas":
                    $ mas_bg_label = "Panel: Dark Backing" if persistent.mp3_mas_bg_dark else "Panel: Transparent"
                    $ mas_bg_bg = Solid("#3e6ea3") if persistent.mp3_mas_bg_dark else Solid("#333333")
                    textbutton mas_bg_label:
                        text_color "#ffffff"
                        background mas_bg_bg
                        hover_background Solid("#5588cc")
                        xalign 0.5
                        action [ToggleField(persistent, "mp3_mas_bg_dark"), Function(renpy.save_persistent), Function(renpy.restart_interaction)]

            # Divider
            frame:
                background Solid("#ffffff22")
                xsize 510
                ysize 2
                xalign 0.5

            # BG and Accent/SliderBar colour side by side
            hbox:
                spacing 20
                xalign 0.5

                vbox:
                    spacing 6
                    text "Background:" color "#aaaaaa" size 16 xalign 0.5
                    hbox:
                        spacing 8
                        textbutton "Pink" action [SetField(persistent, "mp3_bg_color", "#ce0f85d2"), Function(renpy.save_persistent)] background Solid("#ce0f85") hover_background Solid("#ff5fb2")
                        textbutton "Green" action [SetField(persistent, "mp3_bg_color", "#3ea34caa"), Function(renpy.save_persistent)] background Solid("#3ea34c") hover_background Solid("#55cc66")
                    hbox:
                        spacing 8
                        textbutton "Blue" action [SetField(persistent, "mp3_bg_color", "#3e6ea3aa"), Function(renpy.save_persistent)] background Solid("#3e6ea3") hover_background Solid("#5588cc")
                        textbutton "Gray" action [SetField(persistent, "mp3_bg_color", "#444444cc"), Function(renpy.save_persistent)] background Solid("#444444") hover_background Solid("#666666")

                vbox:
                    spacing 6
                    text "Accent (currently for SliderBar only, for now):" color "#aaaaaa" size 16 xalign 0.5
                    hbox:
                        spacing 8
                        textbutton "Aqua" action [SetField(persistent, "mp3_accent_color", "#00cc99"), Function(renpy.save_persistent)] background Solid("#00cc99") hover_background Solid("#00ffbb")
                        textbutton "Gold" action [SetField(persistent, "mp3_accent_color", "#ffaa00"), Function(renpy.save_persistent)] background Solid("#ffaa00") hover_background Solid("#ffcc33")
                    hbox:
                        spacing 8
                        textbutton "Purple" action [SetField(persistent, "mp3_accent_color", "#b066ff"), Function(renpy.save_persistent)] background Solid("#b066ff") hover_background Solid("#cc88ff")
                        textbutton "White" action [SetField(persistent, "mp3_accent_color", "#ffffff"), Function(renpy.save_persistent)] background Solid("#dddddd") hover_background Solid("#ffffff")

            # Divider
            frame:
                background Solid("#ffffff22")
                xsize 510
                ysize 2
                xalign 0.5

            # LCD strip row
            vbox:
                spacing 6
                xalign 0.5
                text "LCD Strip:" color "#aaaaaa" size 16 xalign 0.5
                hbox:
                    spacing 8
                    xalign 0.5
                    textbutton "Black" action [SetField(persistent, "mp3_lcdtrip_color", "#000000"), Function(renpy.save_persistent)] background Solid("#000000") hover_background Solid("#202020c0")
                    textbutton "White" action [SetField(persistent, "mp3_lcdtrip_color", "#ffffff"), Function(renpy.save_persistent)] background Solid("#ffffff") hover_background Solid("#776767c0")
                    textbutton "Red" action [SetField(persistent, "mp3_lcdtrip_color", "#ff0000"), Function(renpy.save_persistent)] background Solid("#ff0000") hover_background Solid("#ff8787c0")
                    textbutton "Orange" action [SetField(persistent, "mp3_lcdtrip_color", "#ff8a05"), Function(renpy.save_persistent)] background Solid("#ff8a05") hover_background Solid("#fdc763c0")

            # Divider
            frame:
                background Solid("#ffffff22")
                xsize 510
                ysize 2
                xalign 0.5

            # Volume
            vbox:
                spacing 4
                xalign 0.5
                text "Volume:" color "#aaaaaa" size 16 xalign 0.5
                bar:
                    adjustment ui.adjustment(range=1.0, value=persistent.mp3_volume, changed=music_set_volume)
                    xsize 400
                    ysize 20
                    xalign 0.5
                    left_bar Frame(Solid("#555555"), 0, 0)
                    right_bar Frame(Solid("#333333"), 0, 0)
                    thumb Frame(Solid("#ffffff"), 0, 0)
                hbox:
                    xsize 400
                    xalign 0.5
                    text "0%" color "#666666" size 13 xalign 0.0
                    text "50%" color "#666666" size 13 xalign 0.5
                    text "100%" color "#666666" size 13 xalign 1.0

            # Divider
            frame:
                background Solid("#ffffff22")
                xsize 510
                ysize 2
                xalign 0.5

            # Rainbow/GamerRGB toggle
            $ rainbow_label = "GamerRGB Mode: ON" if persistent.mp3_rainbow_mode else "GamerRGB Mode: OFF"
            $ rainbow_bg = Solid("#ff00ff") if persistent.mp3_rainbow_mode else Solid("#333333")
            textbutton rainbow_label:
                text_color "#ffffff"
                background rainbow_bg
                hover_background Solid("#ff00ff")
                xalign 0.5
                action [ToggleField(persistent, "mp3_rainbow_mode"), Function(renpy.restart_interaction)]

            # Bottom buttons
            hbox:
                spacing 20
                xalign 0.5
                textbutton "Reset to Default":
                    text_color "#ffffff"
                    background Solid("#333333")
                    hover_background Solid("#df1212")
                    action [
                        SetField(persistent, "mp3_bg_color", "#ce0f85d2"),
                        SetField(persistent, "mp3_accent_color", "#00cc99"),
                        SetField(persistent, "mp3_lcdtrip_color", "#d6ec97"),
                        Function(renpy.notify, "Colors reset to default!"),
                        Function(renpy.save_persistent),
                        Function(renpy.restart_interaction)
                    ]
                textbutton "Close":
                    text_color "#ffffff"
                    background Solid("#333333")
                    hover_background Solid("#df1212")
                    action [Hide("mp3_settings_popup"), Function(renpy.restart_interaction)]


label DevBaka2:

    "Remember... Yun likes hu-tao!"

    jump ch30_loop
    return



label MP3Retrun:
    python:
        mas_HKBDropShield()
    jump ch30_loop
    return



label zoomfixreturn:
    python:
        store.mas_sprites.zoom_level = store.player_zoom
        store.mas_sprites.adjust_zoom()
        mas_HKBDropShield()
    jump ch30_loop
    return
