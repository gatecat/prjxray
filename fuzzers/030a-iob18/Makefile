N := 50
SPECIMENS_DEPS := build/iobanks.txt
include ../fuzzer.mk

database: build/segbits_riob18.db build/segbits_hclk_ioi.db build/segbits_cfg_center_mid.db

build/iobanks.txt: write_io_banks.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ../write_io_banks.tcl

build/segbits_riob18.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 19 -o build/segbits_riob18.rdb $$(find -name segdata_riob18*.txt)

build/segbits_riob18.db: build/segbits_riob18.rdb process_rdb.py bits.dbf
	python3 process_rdb.py build/segbits_riob18.rdb > build/segbits_riob18_processed.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in build/segbits_riob18_processed.rdb --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_riob18.db $$(find -name segdata_riob18*.txt)

build/segbits_hclk_ioi.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 4 -o build/segbits_hclk_ioi.rdb $$(find -name segdata_hclk_ioi.txt)

build/segbits_hclk_ioi.db: build/segbits_hclk_ioi.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db hclk_bits.dbf --seg-fn-in build/segbits_hclk_ioi.rdb --seg-fn-out $@

build/segbits_cfg_center_mid.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 8 -o build/segbits_cfg_center_mid.rdb $$(find -name segdata_cfg_center_mid.txt)

build/segbits_cfg_center_mid.db: build/segbits_cfg_center_mid.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db cfg_center_mid_bits.dbf --seg-fn-in build/segbits_cfg_center_mid.rdb --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_cfg_center_mid.db $$(find -name segdata_cfg_center_mid.txt)

pushdb:
	${XRAY_MERGEDB} riob18 build/segbits_riob18.db
	${XRAY_MERGEDB} mask_riob18 build/mask_riob18.db

	${XRAY_MERGEDB} hclk_ioi build/segbits_hclk_ioi.db

	${XRAY_MERGEDB} cfg_center_mid build/segbits_cfg_center_mid.db
	${XRAY_MERGEDB} mask_cfg_center_mid build/mask_cfg_center_mid.db

.PHONY: database pushdb

