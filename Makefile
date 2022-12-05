# 環境に合せてインストール先とBlenderコマンドを変更してください
DST_BIN=${HOME}/bin
DST_DIR=${HOME}/opt/create-subtitles-movie
BLENDER_COMMAND=/Applications/Blender.app/Contents/MacOS/Blender
FONT_PATH=~/Library/Fonts/BIZUDGothic-Bold.ttf

install: ./build/create-subtitles-movie.sh ./build/config.py
	mkdir -p $(DST_BIN)
	mkdir -p $(DST_DIR)/bin
	mkdir -p $(DST_DIR)/etc
	mkdir -p $(DST_DIR)/lib
	mkdir -p $(DST_DIR)/share/assets

	cp -p src/*.py $(DST_DIR)/lib
	cp -p share/assets/*.blend $(DST_DIR)/share/assets

	cp -p ./build/config.py $(DST_DIR)/etc
	cp -p ./build/create-subtitles-movie.sh $(DST_DIR)/bin
	chmod u+x $(DST_DIR)/bin/create-subtitles-movie.sh
	ln -s $(DST_DIR)/bin/create-subtitles-movie.sh ${DST_BIN}/create-subtitles-movie.sh

./build/create-subtitles-movie.sh: ./build/create-subtitles-movie.sh.tmpl
	cat $< |  sed -e 's#@@@BLENDER_COMMAND@@@#${BLENDER_COMMAND}#' | sed -e 's#@@@DST_DIR@@@#${DST_DIR}#' > $@

./build/config.py: ./build/config.py.tmpl
	cat $< |  sed -e 's#@@@FONT_PATH@@@#${FONT_PATH}#' | sed -e 's#@@@DST_DIR@@@#${DST_DIR}#' > $@

clean: ./build/create-subtitles-movie.sh ./build/config.py
	rm ${DST_BIN}/$(<F)
	rm $^
	rm -r ${DST_DIR}

reinstall:
	make clean
	make install
