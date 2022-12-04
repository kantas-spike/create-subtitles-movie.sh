# 環境に合せてインストール先とBlenderコマンドを変更してください
DST_BIN=${HOME}/bin
DST_DIR=${HOME}/opt/create-subtitles-movie
BLENDER_COMMAND=/Applications/Blender.app/Contents/MacOS/Blender


install: create-subtitles-movie.sh
	mkdir -p $(DST_BIN)
	mkdir -p $(DST_DIR)/bin
	mkdir -p $(DST_DIR)/share
	cp -p src/*.py $(DST_DIR)/share
	cp -p $< $(DST_DIR)/bin
	chmod u+x $(DST_DIR)/bin/$<
	ln -s $(DST_DIR)/bin/$< ${DST_BIN}/$<

./build/create-subtitles-movie.sh: ./build/create-subtitles-movie.sh.tmpl
	cat $< |  sed -e 's#@@@BLENDER_COMMAND@@@#${BLENDER_COMMAND}#' | sed -e 's#@@@DST_DIR@@@#${DST_DIR}#' > $@

clean: ./build/create-subtitles-movie.sh
	rm ${DST_BIN}/$(<F)
	rm $<
	rm -r ${DST_DIR}
