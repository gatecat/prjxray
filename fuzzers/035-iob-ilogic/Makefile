N := 30
include ../fuzzer.mk

database: build/segbits_xioi3.db build/segbits_rioi.db

build/segbits_xioi3.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 6 -o build/segbits_xioi3.rdb $$(find -name segdata_*)

build/segbits_xioi3.db: build/segbits_xioi3.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xioi3.db $$(find -name segdata_*)

build/segbits_rioi.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 6 -o build/segbits_rioi.rdb $$(find -name segdata_*)

build/segbits_rioi.db: build/segbits_rioi.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits_rioi.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_rioi.db $$(find -name segdata_*)


pushdb:
	${XRAY_MERGEDB} lioi3 build/segbits_xioi3.db
	${XRAY_MERGEDB} lioi3_tbytesrc build/segbits_xioi3.db
	${XRAY_MERGEDB} lioi3_tbyteterm build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3 build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3_tbytesrc build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3_tbyteterm build/segbits_xioi3.db
	${XRAY_MERGEDB} mask_lioi3 build/mask_xioi3.db
	${XRAY_MERGEDB} mask_lioi3_tbytesrc build/mask_xioi3.db
	${XRAY_MERGEDB} mask_lioi3_tbyteterm build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3 build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3_tbytesrc build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3_tbyteterm build/mask_xioi3.db

	${XRAY_MERGEDB} rioi build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbytesrc build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbyteterm build/segbits_rioi.db
	${XRAY_MERGEDB} mask_rioi build/mask_xioi.db
	${XRAY_MERGEDB} mask_rioi_tbytesrc build/mask_xioi.db
	${XRAY_MERGEDB} mask_rioi_tbyteterm build/mask_xioi.db

.PHONY: database pushdb

