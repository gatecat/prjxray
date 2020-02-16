N := 5
include ../fuzzer.mk

database: build/segbits_xiob18.db

build/segbits_xiob18.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 1 -M 1 -o build/segbits_xiob18.rdb $$(find -name segdata_?ioi.txt) $$(find -name segdata_?ioi_*.txt)

build/segbits_xiob18.db: build/segbits_xiob18.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xiob18.db $$(find -name segdata_?ioi.txt) $$(find -name segdata_?ioi_*.txt)

pushdb:
	${XRAY_MERGEDB} rioi build/segbits_xiob18.db
	${XRAY_MERGEDB} rioi_tbytesrc build/segbits_xiob18.db
	${XRAY_MERGEDB} rioi_tbyteterm build/segbits_xiob18.db
	${XRAY_MERGEDB} mask_rioi build/mask_xiob18.db
	${XRAY_MERGEDB} mask_rioi_tbytesrc build/mask_xiob18.db
	${XRAY_MERGEDB} mask_rioi_tbyteterm build/mask_xiob18.db

.PHONY: database pushdb

