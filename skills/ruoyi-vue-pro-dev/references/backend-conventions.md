# Backend Conventions (ruoyi-vue-pro)

Use existing module code as the source of truth. Branches differ, so confirm the selected branch, enabled modules, Java version, and Spring Boot version from local files before changing code.

## Package & module layout

- Module root: `yudao-module-<module>/src/main/java/cn/iocoder/yudao/module/<module>/`
- Common subpackages:
  - `controller/admin/**` and `controller/app/**`
  - `controller/.../vo/**` (ReqVO/RespVO/ExcelVO)
  - `service/**` for service interfaces and implementations; follow nearby package placement.
  - `dal/dataobject/**` (DO)
  - `dal/mysql/**` (Mapper)
  - `convert/**` (MapStruct/BeanUtils)
  - `enums/**`, `framework/**`

## Controller conventions

- Annotations: `@Tag`, `@RestController`, `@RequestMapping`, `@Validated` (class), `@Operation` + `@Parameter` (method).
- Security: `@PreAuthorize("@ss.hasPermission('module:resource:action')")`.
- Validation: `@Valid @RequestBody` for body; `@Valid` for query VO.
- Return type: `CommonResult<T>`; use `CommonResult.success(...)`.
- Pagination: `CommonResult<PageResult<RespVO>>` with `PageParam`/`PageResult`.
- Export: use `@ApiAccessLog(operateType = EXPORT)` + `ExcelUtils.write(...)`.

## VO conventions

- Naming: `XxxSaveReqVO`, `XxxUpdateReqVO`, `XxxPageReqVO`, `XxxRespVO`, `XxxSimpleRespVO`, `XxxImportExcelVO`.
- Use `@Schema` on class and fields.
- Validation annotations (`@NotBlank`, `@NotNull`, `@Size`, `@Pattern`, `@Email`, etc.).
- Page VO extends `PageParam` and uses `@DateTimeFormat` for time ranges.
- Export VO uses `@ExcelIgnoreUnannotated`, `@ExcelProperty`, `@DictFormat` if dict.

## DO conventions

- Package: `dal/dataobject`.
- Extend `TenantBaseDO` (tenant data) or `BaseDO` (non-tenant).
- Use `@TableName` and `@TableId`.
- For JSON fields: `@TableField(typeHandler = JacksonTypeHandler.class)` and `autoResultMap = true`.
- If global table: add `@TenantIgnore`.
- Use Lombok (`@Data`, `@Builder`, etc.). Chain setters are enabled by `lombok.accessors.chain=true`.
- Field-level JavaDoc comments are expected.

## Mapper conventions

- Package: `dal/mysql/**`.
- Interface extends `BaseMapperX<DO>`.
- Use `LambdaQueryWrapperX` with `xxxIfPresent` to avoid null conditions.
- `selectPage(reqVO, wrapper)` returns `PageResult<DO>`.

## Service conventions

- Interface and implementation stay under `service/**`; use the module's nearby style instead of forcing an `impl` package.
- Annotate impl with `@Service`, `@Slf4j`.
- For multi-step writes: `@Transactional(rollbackFor = Exception.class)`.
- Use `validateXxx(...)` helper methods; throw `ServiceException` via `ServiceExceptionUtil.exception(ErrorCodeConstants.X)`.
- Prefer `BeanUtils.toBean(...)` and `CollectionUtils.convertList(...)` for mapping.

## Exception handling

- Do not catch in controllers unless needed. Let `GlobalExceptionHandler` translate to `CommonResult`.
- Use `ServiceExceptionUtil.exception(...)` for business errors.
- Error codes live in `module/.../enums/ErrorCodeConstants.java`.

## Data permission & tenant

- Use `@DataPermission(enable = false)` or `DataPermissionUtils.executeIgnore(...)` when necessary.
- Use `TenantBaseDO` for tenant data; `@TenantIgnore` for global data or special endpoints.

## Performance & code quality

- Avoid N+1: prefetch in batch and convert using maps.
- Use `selectList` with `in` for bulk queries; avoid loops with DB calls.
- Use pagination for list APIs; only use `PageParam.PAGE_SIZE_NONE` for export.
- Prefer reuse of `Convert` and `BeanUtils` to reduce duplication.
- Limit report/query endpoints by time window, page size, and returned point count when they may hit large tables.
- For caches, jobs, MQ, file upload, auth, tenant, and data permission, prefer existing `yudao-framework` starters and helpers.
- Add a small focused unit test or module compile check when changing non-trivial service logic.

## Template snippets

### Controller skeleton

```java
@Tag(name = "管理后台 - XXX")
@RestController
@RequestMapping("/module/xxx")
@Validated
public class XxxController {

    @Resource
    private XxxService xxxService;

    @PostMapping("/create")
    @Operation(summary = "新增XXX")
    @PreAuthorize("@ss.hasPermission('module:xxx:create')")
    public CommonResult<Long> create(@Valid @RequestBody XxxSaveReqVO reqVO) {
        return success(xxxService.create(reqVO));
    }

    @PutMapping("/update")
    @Operation(summary = "修改XXX")
    @PreAuthorize("@ss.hasPermission('module:xxx:update')")
    public CommonResult<Boolean> update(@Valid @RequestBody XxxSaveReqVO reqVO) {
        xxxService.update(reqVO);
        return success(true);
    }

    @DeleteMapping("/delete")
    @Operation(summary = "删除XXX")
    @Parameter(name = "id", required = true)
    @PreAuthorize("@ss.hasPermission('module:xxx:delete')")
    public CommonResult<Boolean> delete(@RequestParam("id") Long id) {
        xxxService.delete(id);
        return success(true);
    }

    @GetMapping("/page")
    @Operation(summary = "分页列表")
    @PreAuthorize("@ss.hasPermission('module:xxx:query')")
    public CommonResult<PageResult<XxxRespVO>> page(@Valid XxxPageReqVO reqVO) {
        return success(xxxService.getPage(reqVO));
    }
}
```

### Mapper skeleton

```java
@Mapper
public interface XxxMapper extends BaseMapperX<XxxDO> {
    default PageResult<XxxDO> selectPage(XxxPageReqVO reqVO) {
        return selectPage(reqVO, new LambdaQueryWrapperX<XxxDO>()
                .likeIfPresent(XxxDO::getName, reqVO.getName())
                .eqIfPresent(XxxDO::getStatus, reqVO.getStatus())
                .betweenIfPresent(XxxDO::getCreateTime, reqVO.getCreateTime())
                .orderByDesc(XxxDO::getId));
    }
}
```

### Service skeleton

```java
public interface XxxService {
    Long create(@Valid XxxSaveReqVO reqVO);
    void update(@Valid XxxSaveReqVO reqVO);
    void delete(Long id);
    PageResult<XxxRespVO> getPage(XxxPageReqVO reqVO);
}

@Service
public class XxxServiceImpl implements XxxService {
    @Resource private XxxMapper xxxMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long create(XxxSaveReqVO reqVO) {
        // validate
        // insert
        XxxDO obj = BeanUtils.toBean(reqVO, XxxDO.class);
        xxxMapper.insert(obj);
        return obj.getId();
    }
}
```
