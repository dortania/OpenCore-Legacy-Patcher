CC=clang
OUTPUT=com.dortania.opencore-legacy-patcher.privileged-helper

all: clean release

release: main.m
	$(CC) -framework Foundation -framework Security -arch x86_64 -arch arm64 -mmacosx-version-min=10.9 -o $(OUTPUT) main.m

debug: main.m
	$(CC) -framework Foundation -framework Security -arch x86_64 -arch arm64 -mmacosx-version-min=10.9 -o $(OUTPUT) main.m -DDEBUG

clean:
	/bin/rm -f $(OUTPUT)