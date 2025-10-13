# auto submod update

# -- you can tell BonkAMon was here...

# Register the submod
init -990 python:
    store.mas_submod_utils.Submod(
        author="Phazeee",
        name="MP3MasPlayer",
        description="Mp3 Styled MAS Player! Listen to music with her you absolute gamer.",
        version="0.0.2",
    )


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
        if store.mas_submod_utils.isSubmodInstalled("Open World"):
                frame:
                    area (310, 550, 202, 65)
                    style "mas_extra_menu_frame"
                    if persistent._mas_in_idle_mode == True:
                        textbutton ("Open World"):
                            xalign 0.5
                            yalign 0.5
                            action NullAction()
                    else:
                        textbutton ("Open World"):
                            xalign 0.5
                            yalign 0.5
                            action [Hide("mas_extramenu_area"), Jump("view_OW")] hover_sound gui.hover_sound
                frame:        
                    area (520, 639, 202, 65)
                    style "mas_extra_menu_frame"
                    if persistent._mas_in_idle_mode == True:
                        textbutton ("MP3 Player!"):
                            xalign 0.5
                            yalign 0.5
                            action NullAction()
                    else:
                        textbutton ("MP3 Player!"):
                            xalign 0.5
                            yalign 0.5
                            action [Hide("mas_extramenu_area"), Jump("MP3PlayerMenu")] hover_sound gui.hover_sound

        if store.mas_submod_utils.isSubmodInstalled("BonkAMon"):
                frame:
                    area (310, 639, 202, 65)
                    style "mas_extra_menu_frame"
                    if persistent._mas_in_idle_mode == True:
                        textbutton ("Bonk Monika"):
                            xalign 0.5
                            yalign 0.5
                            action NullAction()
                    else:
                        textbutton ("Bonk Monika"):
                            xalign 0.5
                            yalign 0.5
                            action [Hide("mas_extramenu_area"), Jump("view_bonkmenu")] hover_sound gui.hover_sound
                frame:        
                    area (520, 639, 202, 65)
                    style "mas_extra_menu_frame"
                    if persistent._mas_in_idle_mode == True:
                        textbutton ("MP3 Player!"):
                            xalign 0.5
                            yalign 0.5
                            action NullAction()
                    else:
                        textbutton ("MP3 Player!"):
                            xalign 0.5
                            yalign 0.5
                            action [Hide("mas_extramenu_area"), Jump("MP3PlayerMenu")] hover_sound gui.hover_sound
                       
        else:
            frame:
                area (308, 639, 202, 65)
                style "mas_extra_menu_frame"
                if persistent._mas_in_idle_mode == True:
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

# Persistent variables
default music_track_list = []
default music_current_index = 0
default music_is_playing = False

init python:
    import os

    SUPPORTED_AUDIO_EXTS = [".mp3", ".ogg", ".wav", ".flac", ".opus"]

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
                    renpy.log("MP3Mas: Created missing music folder at: {}".format(full_path))
                except Exception as e:
                    renpy.log("MP3Mas: Failed to create folder: {}".format(e))
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
        return music_track_list

    def music_play(index=None):
    # Play a track by index, or resume current song that is playing. DID YOU KNOW RENPY HAS WEIRD AUDIO DOCUMENTATION??
        global music_current_index, music_is_playing
        if not music_track_list:
            music_load_tracks()
        if index is not None:
            music_current_index = index
        if not music_track_list:
            return
    
    # Check if the music is paused
        if renpy.music.is_playing(channel="music") and not music_is_playing:
            renpy.music.set_pause(False, channel="music")
        else:
            file = MUSIC_FOLDER + music_track_list[music_current_index]
            renpy.music.play(file, channel="music", loop=False)
    
        music_is_playing = True

    def music_stop():
        renpy.music.stop(channel="music")
        global music_is_playing
        music_is_playing = False

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

    def music_prev():
        global music_current_index
        if not music_track_list:
            return
        music_current_index = (music_current_index - 1) % len(music_track_list)
        music_play(music_current_index)

# THE ACTUAL UI BELOW! Fear my terrible design for i have no [BLEEP]ing clue how to design for the life of me!

screen mp3_player_screen():
    tag menu
    modal True
    zorder 100

    # Outer player casing
    frame:
        background Solid("#ce0f85d2")
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
                    background Solid("#d6ec97")
                    xalign 0.5
                    xpadding 10
                    ypadding 6
                    # Playback lines here.
                    $ display_line = status_text + " " + current_track #if status_text != "Stopped" else "Song is stopped!"
                    text display_line color "#ffffff" size 18 xalign 0.5

                # simple static progress bar... hint. it does nothing but look pretty... for now.
                bar:
                    value 0.5
                    xsize 400
                    ysize 10
                    xalign 0.5
                    left_bar Frame(Solid("#00cc99"), 0, 0)
                    right_bar Frame(Solid("#333333"), 0, 0)
                    thumb None

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
                
            
            #textbutton "?":
            #  text_color "#ffffff"
            # background Solid("#333333")
            # hover_background Solid("#00cc99")
            #  xalign 0.5
            #  action Show("mp3_info_popup")

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

#labels land

label ViewMP3Menu2:
    python:
        music_load_tracks()
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
        ysize 320
        xpadding 20
        ypadding 20
        vbox:
            spacing 12
            text "MP3Mas Player Help" color "#66ffcc" size 26 xalign 0.5
            text "• Place your music files in: game/submods/MP3Mas/music/" color "#ffffff" size 18
            text "• Supports: MP3, OGG, WAV, FLAC, OPUS" color "#ffffff" size 18
            text "• Use the Play, Pause, Stop, Next, and Prev buttons to control playback." color "#ffffff" size 18
            text "• Monika will remember your last played song!" color "#ffffff" size 18

            textbutton "Close":
                text_color "#ffffff"
                background Solid("#333333")
                hover_background Solid("#df1212")
                xalign 0.5
                action Hide("mp3_info_popup")





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
